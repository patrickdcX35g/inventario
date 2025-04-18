from django.db import models

# Create your models here.

class Producto(models.Model):
    TIPO_ITEM_CHOICES = [
        ('BIEN', 'Bien'),
        ('SERVICIO', 'Servicio'),
    ]

    codigo = models.CharField(max_length=20, unique=True)
    codigo_barras = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_ITEM_CHOICES)
    unidad = models.CharField(max_length=20)
    marca = models.CharField(max_length=50, blank=True, null=True)
    estado = models.CharField(max_length=20, default='Activo')  # Activo / Inactivo

    # Nuevo campo agregado
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Precio de venta

    def __str__(self):
        return f"{self.codigo} - {self.descripcion}"
