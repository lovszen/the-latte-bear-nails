from django.urls import path
from . import views_core, views_presupuestos, views_pagos, views_carrito

urlpatterns = [
    path('', views_core.home, name='home'),
    path('payment/success/', views_core.payment_success, name='payment_success'),
    path('payment/failure/', views_core.payment_failure, name='payment_failure'),
    path('payment/pending/', views_core.payment_pending, name='payment_pending'),
    
    path('budgets/', views_presupuestos.budgets_list, name='budgets_list'),
    path('budgets/create/', views_presupuestos.create_budget, name='create_budget'),
    path('budget/create-from-cart/', views_presupuestos.create_budget_from_cart, name='create_budget_from_cart'),
    path('budgets/<int:budget_id>/', views_presupuestos.view_budget, name='view_budget'),
    path('budgets/<int:budget_id>/pay/', views_pagos.crear_pago_presupuesto, name='crear_pago_presupuesto'),
    
    path('api/payments/create/', views_pagos.crear_pago_carrito_js, name='crear_pago_carrito'),
    path('carrito/detalle/', views_carrito.detalle_carrito, name='detalle_carrito'),
]