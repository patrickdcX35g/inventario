from django.db import models

# Create your models here.

class Almacen(models.Model):
    nombre = models.CharField(max_length=100)
    sucursal = models.ForeignKey('Sucursal', on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
    
class Sucursal(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre    