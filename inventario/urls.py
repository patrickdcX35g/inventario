# inventario/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('registrar-compra/', views.registrar_compra, name='registrar_compra'),
    path('', views.vista_inventario, name='vista_inventario'),
]
