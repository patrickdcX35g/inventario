from django.db import models
from products.models import Producto
from sucursales.models import Sucursal,Almacen

# Create your models here.

class Compra(models.Model):
    sucursal = models.ForeignKey(Sucursal, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    motivo = models.CharField(max_length=100, default='COMPRAS')
    fecha = models.DateField()

    proveedor = models.CharField(max_length=100, blank=True, null=True)
    moneda = models.CharField(max_length=10, blank=True, null=True)
    tipo_documento = models.CharField(max_length=50, blank=True, null=True)
    serie = models.CharField(max_length=10, blank=True, null=True)
    correlativo = models.CharField(max_length=10, blank=True, null=True)
    tipo_documento_adicional = models.CharField(max_length=50, blank=True, null=True)
    serie_adicional = models.CharField(max_length=10, blank=True, null=True)
    correlativo_adicional = models.CharField(max_length=10, blank=True, null=True)

    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Compra {self.id} - {self.fecha}"
    

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.FloatField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    igv = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    observacion = models.TextField(blank=True, null=True)

    @property
    def total(self):
        return self.precio_unitario + self.igv

    def __str__(self):
        return f"{self.producto.descripcion} x {self.cantidad}"    