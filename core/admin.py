from django.contrib import admin
from .models import Budget, BudgetItem, TelegramChatMessage, PersonalizedRequest

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'customer_name', 'customer_email', 'total_amount', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'customer_name', 'customer_email']

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['budget', 'product', 'quantity', 'price', 'subtotal']
    list_filter = ['budget']

@admin.register(PersonalizedRequest)
class PersonalizedRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'forma', 'largo', 'medidas', 'status', 'created_at', 'related_budget']
    list_filter = ['status', 'forma', 'created_at']
    search_fields = ['user__username', 'forma', 'medidas']
    readonly_fields = ['user', 'related_budget']
    actions = ['mark_as_quoted']

    def mark_as_quoted(self, request, queryset):
        queryset.update(status='quoted')
    mark_as_quoted.short_description = "Marcar solicitudes como presupuestadas"


@admin.register(TelegramChatMessage)
class TelegramChatMessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'sender_email', 'message_type', 'timestamp', 'replied']
    list_filter = ['message_type', 'timestamp', 'replied']
    search_fields = ['sender_name', 'sender_email', 'message']
    readonly_fields = ['sender_name', 'sender_email', 'message', 'image_url', 'timestamp', 'message_type', 'admin_user']
    ordering = ['-timestamp']