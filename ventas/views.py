from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404,redirect
from .models import Venta, DetalleVenta, DetalleCompra
from products.models import Producto
from inventario.models import Stock,Almacen
from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum
from .models import Venta, DetalleVenta
from products.models import Producto
from inventario.models import Stock, Almacen,Caja
from django.db.models import F, Sum, DecimalField

from django.shortcuts import render, redirect, get_object_or_404


def registrar_venta(request):
    # Verificar si hay una caja abierta
    caja_abierta = Caja.objects.filter(abierto=True).first()

    if not caja_abierta:
        # Si no hay caja abierta, redirigir a la página de abrir caja
        return redirect('abrir_caja')

    # Obtener cada producto con su stock por almacén (sin agrupar)
    productos_con_stock = (
        Stock.objects
        .filter(cantidad__gt=0, producto__estado='Activo')
        .select_related('producto', 'almacen')
    )

    productos = [
        {
            'id': s.producto.id,
            'descripcion': s.producto.descripcion,
            'codigo': s.producto.codigo,
            'stock': s.cantidad,
            'almacen_id': s.almacen.id,
            'almacen_nombre': s.almacen.nombre
        }
        for s in productos_con_stock
    ]

    almacenes = Almacen.objects.all()

    if request.method == 'POST':
        cliente = request.POST['cliente']
        fecha = request.POST['fecha']
        productos_ids = request.POST.getlist('productos[]')
        almacenes_ids = request.POST.getlist('almacenes[]')
        cantidades = request.POST.getlist('cantidades[]')

        if not productos_ids or not cantidades or not almacenes_ids:
            return render(request, 'ventas/registrar_venta.html', {
                'productos': productos,
                'almacenes': almacenes,
                'error': 'Debe seleccionar al menos un producto con cantidad.'
            })

        # Crear la venta asociada a la caja abierta
        venta = Venta.objects.create(cliente=cliente, fecha=fecha, caja=caja_abierta)

        for producto_id, almacen_id, cantidad_str in zip(productos_ids, almacenes_ids, cantidades):
            producto = get_object_or_404(Producto, id=producto_id)
            almacen_id = int(almacen_id)
            cantidad = float(cantidad_str)

            try:
                # Obtener el stock del producto en el almacén seleccionado
                stock = Stock.objects.get(producto=producto, almacen_id=almacen_id)

                # Verificar que haya suficiente stock
                if stock.cantidad >= cantidad:
                    stock.cantidad -= cantidad  # Descontar el stock
                    stock.save()
                else:
                    # Si no hay suficiente stock, mostrar un mensaje de error
                    return render(request, 'ventas/registrar_venta.html', {
                        'productos': productos,
                        'almacenes': almacenes,
                        'error': f'No hay suficiente stock para {producto.descripcion} en el almacén {stock.almacen.nombre}.'
                    })
            except Stock.DoesNotExist:
                # Si no se encuentra stock para el producto en el almacén, mostrar error
                return render(request, 'ventas/registrar_venta.html', {
                    'productos': productos,
                    'almacenes': almacenes,
                    'error': f'No se encontró stock para {producto.descripcion} en el almacén seleccionado.'
                })

            # Crear el detalle de la venta
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad
            )

        # Redirigir a una página de confirmación con la venta
        return render(request, 'ventas/venta_confirmada.html', {'venta': venta})

    # Si es una solicitud GET, renderizar el formulario
    return render(request, 'ventas/registrar_venta.html', {
        'productos': productos,
        'almacenes': almacenes,
        'caja_abierta': caja_abierta
    })

def productos_por_almacen(request, almacen_id):
    if almacen_id == "todos":
        stocks = (
            Stock.objects
            .filter(producto__estado='Activo', cantidad__gt=0)
            .select_related('producto', 'almacen')
        )
    else:
        stocks = (
            Stock.objects
            .filter(almacen_id=almacen_id, producto__estado='Activo', cantidad__gt=0)
            .select_related('producto', 'almacen')
        )

    data = [
        {
            'id': stock.producto.id,
            'descripcion': stock.producto.descripcion,
            'codigo': stock.producto.codigo,
            'stock': stock.cantidad,
            'almacen_id': stock.almacen.id,
            'almacen_nombre': stock.almacen.nombre
        }
        for stock in stocks
    ]

    return JsonResponse(data, safe=False)

def abrir_caja(request):
    # Verificar si ya hay una caja abierta
    caja_abierta = Caja.objects.filter(abierto=True).first()  # Obtener la primera caja abierta

    if caja_abierta:
        return redirect('registrar_venta')  # Redirigir si ya hay una caja abierta

    if request.method == 'POST':
        monto_inicial = request.POST['monto_inicial']
        # Crear una nueva caja abierta con el monto inicial
        Caja.objects.create(abierto=True, monto_inicial=monto_inicial, monto_total=monto_inicial)
        return redirect('registrar_venta')  # Redirigir a la página de registrar venta después de abrir la caja

    return render(request, 'ventas/abrir_caja.html')

def cerrar_caja(request, caja_id):
    caja = get_object_or_404(Caja, pk=caja_id)

    total_vendido = DetalleVenta.objects.filter(
        venta__caja_id=caja_id
    ).aggregate(
        total=Sum(F('cantidad') * F('producto__precio'), output_field=DecimalField())
    )['total'] or 0

    caja.monto_total = caja.monto_inicial + total_vendido
    caja.abierto = False
    caja.save()

    context = {
        'caja': caja,
        'total_vendido': total_vendido,
    }
    return render(request, 'ventas/cierre_caja.html', context)

from django.db.models import Sum
from django.shortcuts import render
from ventas.models import DetalleVenta
from products.models import Producto
import pandas as pd
from datetime import timedelta
from sklearn.linear_model import LinearRegression

def prediccion_productos(request):
    # Ranking actual (TOP 10)
    ranking = (DetalleVenta.objects
               .values('producto__descripcion')
               .annotate(total_vendido=Sum('cantidad'))
               .order_by('-total_vendido')[:10])

    # Datos históricos por fecha y producto
    data = (DetalleVenta.objects
            .values('producto__id', 'producto__descripcion', 'venta__fecha')
            .annotate(total=Sum('cantidad')))

    df = pd.DataFrame(data)
    if df.empty:
        return render(request, 'ventas/prediccion_productos.html', {'ranking': ranking, 'predicciones': []})

    df['venta__fecha'] = pd.to_datetime(df['venta__fecha'])
    df.sort_values(by='venta__fecha', inplace=True)

    predicciones = []

    for producto_id in df['producto__id'].unique():
        df_producto = df[df['producto__id'] == producto_id]
        df_producto = df_producto.groupby('venta__fecha')['total'].sum().reset_index()

        df_producto['dias'] = (df_producto['venta__fecha'] - df_producto['venta__fecha'].min()).dt.days
        X = df_producto[['dias']]
        y = df_producto['total']

        if len(X) > 1:  # Asegura que hay suficientes datos para entrenar
            modelo = LinearRegression()
            modelo.fit(X, y)

            dias_futuros = (df_producto['dias'].max() + 30)
            prediccion = modelo.predict([[dias_futuros]])[0]

            descripcion = df[df['producto__id'] == producto_id]['producto__descripcion'].iloc[0]
            predicciones.append({
                'descripcion': descripcion,
                'prediccion': round(prediccion, 2)
            })

    predicciones = sorted(predicciones, key=lambda x: x['prediccion'], reverse=True)[:10]

    return render(request, 'ventas/prediccion_productos.html', {
        'ranking': ranking,
        'predicciones': predicciones
    })


    
