from django.contrib import admin

# Register your models here.

from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display=('nombre', 'forma', 'tamaño', 'color_principal', 'precio')
    list_filter=('forma', 'tamaño', 'color_principal')