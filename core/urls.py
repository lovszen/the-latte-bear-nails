from django.urls import path
from . import views_core, views_presupuestos, views_pagos, views_carrito
from .views_telegram import BudgetCreateView
from .views_telegram_chat import TelegramChatCreateView, TelegramChatListView, TelegramChatAdminReplyView, get_user_messages, get_my_messages, admin_chat_view, send_telegram_message, upload_image_to_cloudinary

urlpatterns = [
    path('', views_core.home, name='home'),
    path('payment/success/', views_core.payment_success, name='payment_success'),
    path('payment/failure/', views_core.payment_failure, name='payment_failure'),
    path('payment/pending/', views_core.payment_pending, name='payment_pending'),
    
    # URLs DE ADMINISTRACIÓN (SIN PREFIJO 'admin/' DUPLICADO)
    path('productos/', views_presupuestos.admin_productos_lista, name='admin_productos'),
    path('productos/agregar/', views_presupuestos.admin_agregar_producto, name='admin_agregar_producto'),
    path('solicitudes/', views_presupuestos.admin_solicitudes_pendientes, name='admin_solicitudes'),
    path('editar-producto/<int:producto_id>/', views_presupuestos.admin_editar_producto, name='admin_editar_producto'),
    path('eliminar-producto/<int:producto_id>/', views_presupuestos.admin_eliminar_producto, name='admin_eliminar_producto'),
    path('dashboard/', views_presupuestos.admin_dashboard, name='admin_dashboard'),
    path('todos-presupuestos/', views_presupuestos.admin_todos_presupuestos, name='admin_todos_presupuestos'),
    
    # URLs ESPECÍFICAS DE ADMIN PARA PRESUPUESTOS
    path('gestion-presupuestos/', views_presupuestos.admin_gestion_presupuestos, name='admin_gestion_presupuestos'),
    path('presupuestos/eliminar-masivo/', views_presupuestos.eliminar_presupuestos_masivos, name='eliminar_presupuestos_masivos'),
    path('presupuestos/limpiar-prueba/', views_presupuestos.limpiar_presupuestos_prueba, name='limpiar_presupuestos_prueba'),
    path('budgets/<int:budget_id>/', views_presupuestos.admin_view_budget, name='admin_view_budget'),
    path('budgets/<int:budget_id>/delete/', views_presupuestos.admin_delete_budget, name='admin_delete_budget'),
    
    # URLs GENERALES DE PRESUPUESTOS (PARA USUARIOS NORMALES)
    path('budgets/', views_presupuestos.budgets_list, name='budgets_list'),
    path('budgets/create/', views_presupuestos.create_budget, name='create_budget'),
    path('budgets/<int:budget_id>/', views_presupuestos.view_budget, name='view_budget'),
    path('budgets/<int:budget_id>/edit/', views_presupuestos.edit_budget, name='edit_budget'),
    path('budgets/<int:budget_id>/delete/', views_presupuestos.delete_budget, name='delete_budget'),  # ← ¡AGREGAR ESTA LÍNEA!
    path('budgets/<int:budget_id>/download/', views_presupuestos.download_budget, name='download_budget'),
    path('budgets/<int:budget_id>/generate/', views_presupuestos.generate_budget, name='generate_budget'),
    
    # URLs DE PAGOS
    path('budgets/<int:budget_id>/pay/', views_pagos.crear_pago_presupuesto, name='crear_pago_presupuesto'),
    path('budgets/<int:budget_id>/pay-mp/', views_pagos.mp_create_payment, name='mp_create_payment'),
    
    # URLs DE CONVERSIÓN Y CARRITO
    path('requests/<int:request_id>/convert/', views_presupuestos.convert_request_to_budget, name='convert_request_to_budget'),
    path('budget/create-from-cart/', views_presupuestos.create_budget_from_cart, name='create_budget_from_cart'),
    path('carrito/detalle/', views_carrito.detalle_carrito, name='detalle_carrito'),
    
    # URLs DE API/TELEGRAM
    path('api/budgets/create/', BudgetCreateView.as_view(), name='telegram_budget_create'),
    path('api/chat/send/', send_telegram_message, name='send_telegram_message'),
    path('api/chat/create/', TelegramChatCreateView.as_view(), name='telegram_chat_create'),
    path('api/chat/list/', TelegramChatListView.as_view(), name='telegram_chat_list'),
    path('api/chat/reply/', TelegramChatAdminReplyView.as_view(), name='telegram_chat_admin_reply'),
    path('api/chat/messages/<str:email>/', get_user_messages, name='get_user_messages'),
    path('api/chat/my-messages/', get_my_messages, name='get_my_messages'),
    path('api/chat/upload-image/', upload_image_to_cloudinary, name='upload_image_to_cloudinary'),
    path('api/payments/create/', views_pagos.crear_pago_carrito_js, name='crear_pago_carrito'),
    
    # URLs DE CHAT
    path('admin_chat/', admin_chat_view, name='admin_chat'),
    path('chat/', views_core.chat_view, name='chat'),
]