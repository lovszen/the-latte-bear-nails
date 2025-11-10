from django.urls import path
from core.views_core import home, payment_success, payment_failure, payment_pending
from core.views_presupuestos import budgets_list, create_budget, create_budget_from_cart, view_budget
from core.views_pagos import crear_pago_presupuesto, crear_pago_carrito_js
from core.views_telegram import BudgetCreateView
from core.views_telegram_chat import TelegramChatCreateView, TelegramChatListView, TelegramChatAdminReplyView, get_user_messages, send_telegram_message, upload_image_to_cloudinary

urlpatterns = [
    path('', home, name='home'),
    path('budgets/', budgets_list, name='budgets_list'),
    path('budgets/create/', create_budget, name='create_budget'),
    path('budget/create-from-cart/', create_budget_from_cart, name='create_budget_from_cart'),
    path('budgets/<int:budget_id>/', view_budget, name='view_budget'),
    path('budgets/<int:budget_id>/pay/', crear_pago_presupuesto, name='crear_pago_presupuesto'),
    path('api/payments/create/', crear_pago_carrito_js, name='crear_pago_carrito'),
    path('api/budgets/create/', BudgetCreateView.as_view(), name='telegram_budget_create'),
    path('api/chat/send/', send_telegram_message, name='send_telegram_message'),
    path('api/chat/create/', TelegramChatCreateView.as_view(), name='telegram_chat_create'),
    path('api/chat/list/', TelegramChatListView.as_view(), name='telegram_chat_list'),
    path('api/chat/reply/', TelegramChatAdminReplyView.as_view(), name='telegram_chat_admin_reply'),
    path('api/chat/messages/<str:email>/', get_user_messages, name='get_user_messages'),
    path('api/chat/upload-image/', upload_image_to_cloudinary, name='upload_image_to_cloudinary'),
    path('payment/success/', payment_success, name='payment_success'),
    path('payment/failure/', payment_failure, name='payment_failure'),
    path('payment/pending/', payment_pending, name='payment_pending'),
]
