from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'forma', 'tamaño', 'color_principal', 'color_secundario']
    list_filter = ['forma', 'tamaño', 'color_principal', 'color_secundario']
    search_fields = ['nombre']