from django.shortcuts import render,redirect
from .forms import ProductoForm
from .models import Producto
from django.http import JsonResponse
# Create your views here.

def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('agregar_producto')
    else:
        form = ProductoForm()
    return render(request, 'productos/agregar_producto.html', {'form': form})



from django.http import JsonResponse
from .models import Producto

def buscar_productos(request):
    termino = request.GET.get('q', '').lower()

    if termino:
        productos = Producto.objects.filter(descripcion__icontains=termino)
    else:
        productos = Producto.objects.none()

    productos_data = [{'id': producto.id, 'descripcion': producto.descripcion} for producto in productos]

    return JsonResponse({'productos': productos_data})