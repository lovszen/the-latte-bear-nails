from django.db import models
from cloudinary.models import CloudinaryField

class Producto(models.Model):
    color_choices = [
        ('rosa', 'Rosa'),
        ('rojo', 'Rojo'),
        ('amarillo', 'Amarillo'),
        ('negro', 'Negro'),
        ('plateado', 'Plateado'),
        ('blanco', 'Blanco'),
        ('azul', 'Azul'),
        ('celeste', 'Celeste'),
        ('naranja', 'Naranja'),
        ('violeta', 'Violeta'),
        ('dorado', 'Dorado'),
        ('verde', 'Verde'),
        ('transparente', 'Transparente'),
    ]

    forma_choices = [
        ('cuadrada', 'Cuadrada'),
        ('almendra', 'Almendra'),
        ('redonda', 'Redonda'),
        ('stiletto', 'Stiletto'),
        ('coffin', 'Coffin'),
        ('ballerina', 'Ballerina'),
    ]

    tamaño_choices = [
        ('xs', 'Tamaño 1, xs'),
        ('s', 'Tamaño 2, s'),
        ('m', 'Tamaño 3, m'),
        ('l', 'Tamaño 4, l'),
    ]

    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = CloudinaryField('imagen')  
    descripcion = models.TextField(blank=True)
    forma = models.CharField(max_length=20, choices=forma_choices, default='almendra')
    tamaño = models.CharField(max_length=10, choices=tamaño_choices, default='s')
    color_principal = models.CharField(max_length=20, choices=color_choices)
    color_secundario = models.CharField(max_length=20, choices=color_choices, blank=True, null=True)
    
    def __str__(self):
        if self.color_secundario:
            return f"{self.nombre} ({self.color_principal} + {self.color_secundario})"
        return f"{self.nombre} ({self.color_principal})"