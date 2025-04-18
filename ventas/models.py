from django.db import models
from compras.models import DetalleCompra  # Importamos el modelo DetalleCompra
from decimal import Decimal
from inventario.models import Caja

class Venta(models.Model):
    fecha = models.DateField()
    cliente = models.CharField(max_length=100)
    caja = models.ForeignKey(Caja, on_delete=models.CASCADE)

    def __str__(self):
        return f"Venta {self.id} - {self.fecha}"

    @property
    def total(self):
        return sum(detalle.total for detalle in self.detalles.all())

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey('products.Producto', on_delete=models.CASCADE)
    cantidad = models.FloatField()
    detalle_compra = models.ForeignKey(DetalleCompra, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def precio_unitario(self):
        return self.producto.precio or Decimal(0)

    @property
    def total(self):
        return Decimal(self.cantidad) * self.precio_unitario

    def __str__(self):
        return f"{self.producto.descripcion} x {self.cantidad} - {self.total}"
