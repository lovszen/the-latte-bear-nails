from django.contrib import admin
from .models import Budget, BudgetItem

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'customer_name', 'customer_email', 'total_amount', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'customer_name', 'customer_email']

@admin.register(BudgetItem)
class BudgetItemAdmin(admin.ModelAdmin):
    list_display = ['budget', 'product', 'quantity', 'price', 'subtotal']
    list_filter = ['budget']
