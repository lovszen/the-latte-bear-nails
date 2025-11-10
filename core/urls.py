from django.urls import path
from . import views_core, views_presupuestos, views_pagos, views_carrito
from .views_telegram import BudgetCreateView
from .views_telegram_chat import TelegramChatCreateView, TelegramChatListView, TelegramChatAdminReplyView, get_user_messages, get_my_messages, admin_chat_view, send_telegram_message, upload_image_to_cloudinary

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
    
    # Telegram integration
    path('api/budgets/create/', BudgetCreateView.as_view(), name='telegram_budget_create'),
    path('api/chat/send/', send_telegram_message, name='send_telegram_message'),
    path('api/chat/create/', TelegramChatCreateView.as_view(), name='telegram_chat_create'),
    path('api/chat/list/', TelegramChatListView.as_view(), name='telegram_chat_list'),
    path('api/chat/reply/', TelegramChatAdminReplyView.as_view(), name='telegram_chat_admin_reply'),
    path('api/chat/messages/<str:email>/', get_user_messages, name='get_user_messages'),
    path('api/chat/my-messages/', get_my_messages, name='get_my_messages'),
    path('api/chat/upload-image/', upload_image_to_cloudinary, name='upload_image_to_cloudinary'),
    
    path('api/payments/create/', views_pagos.crear_pago_carrito_js, name='crear_pago_carrito'),
    path('admin_chat/', admin_chat_view, name='admin_chat'),
    path('chat/', views_core.chat_view, name='chat'),
    path('carrito/detalle/', views_carrito.detalle_carrito, name='detalle_carrito'),
]