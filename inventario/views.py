from django.shortcuts import render, redirect
from .forms import CompraForm, DetalleCompraFormSet
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Stock
from sucursales.models import Sucursal,Almacen
from products.models import Producto

def registrar_compra(request):
    if request.method == 'POST':
        form = CompraForm(request.POST)
        formset = DetalleCompraFormSet(request.POST)

        if formset.total_form_count() == 0:
            return JsonResponse({
                'success': False,
                'error': 'Agrega al menos un producto en el detalle de compra.',
                'form_errors': {},
                'formset_errors': []
            })

        if form.is_valid() and formset.is_valid():
            compra = form.save()
            detalles = formset.save(commit=False)
            for detalle in detalles:
                detalle.compra = compra
                detalle.save()

                stock, _ = Stock.objects.get_or_create(
                    producto=detalle.producto,
                    almacen=compra.almacen,
                    defaults={'cantidad': 0}
                )
                stock.cantidad += detalle.cantidad
                stock.save()

            return JsonResponse({'success': True})

        else:
            form_errors = {field: list(errors) for field, errors in form.errors.items()}
            formset_errors = [
                {field: list(errors) for field, errors in form.errors.items()}
                for form in formset.forms if form.errors
            ]

            return JsonResponse({
                'success': False,
                'error': 'Revisa los campos',
                'form_errors': form_errors,
                'formset_errors': formset_errors
            })

    else:
        form = CompraForm()
        formset = DetalleCompraFormSet()
        return render(request, 'inventarios/registrar_compra.html', {
            'form': form,
            'formset': formset
        })
from .models import Stock
from django.db.models import Prefetch

def vista_inventario(request):
    sucursal_id = request.GET.get('sucursal')
    almacen_id = request.GET.get('almacen')

    stocks = Stock.objects.select_related('producto', 'almacen')

    if sucursal_id:
        stocks = stocks.filter(almacen__sucursal__id=sucursal_id)
    if almacen_id:
        stocks = stocks.filter(almacen__id=almacen_id)

    sucursales = Sucursal.objects.all()
    almacenes = Almacen.objects.all()

    return render(request, 'inventarios/ver_inventario.html', {
        'stocks': stocks,
        'sucursales': sucursales,
        'almacenes': almacenes,
    })
