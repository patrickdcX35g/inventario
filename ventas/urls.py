# ventas/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('registrar/', views.registrar_venta, name='registrar_venta'),
    path('prediccion/', views.prediccion_productos, name='prediccion_productos'),
    path('productos-por-almacen/<int:almacen_id>/', views.productos_por_almacen, name='productos_por_almacen'),
    path('abrir_caja/', views.abrir_caja, name='abrir_caja'),
    path('cerrar_caja/<int:caja_id>/', views.cerrar_caja, name='cerrar_caja'),

    # Otras rutas para la aplicación de ventas pueden ir aquí
]