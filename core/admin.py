from django.contrib import admin
from .models import Budget, BudgetItem, TelegramChatMessage

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'customer_name', 'customer_email', 'total_amount', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'customer_name', 'customer_email']

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['budget', 'product', 'quantity', 'price', 'subtotal']
    list_filter = ['budget']

@admin.register(TelegramChatMessage)
class TelegramChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'sender_email', 'message_type', 'timestamp', 'replied']
    list_filter = ['message_type', 'timestamp', 'replied']
    search_fields = ['sender_name', 'sender_email', 'message']
    readonly_fields = ['sender_name', 'sender_email', 'message', 'image_url', 'timestamp', 'message_type', 'admin_user']
    ordering = ['-timestamp']
