from django.urls import path
from . import views_productos

urlpatterns = [
    path('tienda/', views_productos.lista_productos, name='tienda'),
    path('api/productos/<int:producto_id>/', views_productos.detalle_producto_api, name='detalle_producto_api'),
]