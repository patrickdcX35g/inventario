from django.db import models
from products.models import Producto
from sucursales.models import Almacen

# Create your models here.

class Stock(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    almacen = models.ForeignKey(Almacen, on_delete=models.CASCADE)
    cantidad = models.FloatField(default=0)

    class Meta:
        unique_together = ('producto', 'almacen')

    def __str__(self):
        return f"{self.producto.descripcion} - {self.almacen.nombre}: {self.cantidad}"



class Caja(models.Model):
    abierto = models.BooleanField(default=False)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Caja {'Abierta' if self.abierto else 'Cerrada'}"        