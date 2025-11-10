from django.urls import path
from core.views.core.views_core import home, payment_success, payment_failure, payment_pending
from core.views.presupuestos.views_presupuestos import budgets_list, create_budget, create_budget_from_cart, view_budget
from core.views.pagos.views_pagos import crear_pago_presupuesto, crear_pago_carrito_js

urlpatterns = [
    path('', home, name='home'),
    path('budgets/', budgets_list, name='budgets_list'),
    path('budgets/create/', create_budget, name='create_budget'),
    path('budget/create-from-cart/', create_budget_from_cart, name='create_budget_from_cart'),
    path('budgets/<int:budget_id>/', view_budget, name='view_budget'),
    path('budgets/<int:budget_id>/pay/', crear_pago_presupuesto, name='crear_pago_presupuesto'),
    path('api/payments/create/', crear_pago_carrito_js, name='crear_pago_carrito'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/failure/', payment_failure, name='payment_failure'),
    path('payment/pending/', payment_pending, name='payment_pending'),
]
