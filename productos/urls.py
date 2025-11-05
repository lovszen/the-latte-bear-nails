# productos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('tienda/', views.lista_productos, name='tienda'),
    path('api/budget/create/', views.create_budget_from_cart, name='create_budget_from_cart'),
    path('api/payments/create/', views.crear_pago_carrito_js, name='mp_create_from_cart_js'),
]