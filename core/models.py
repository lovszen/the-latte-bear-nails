from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} - {self.customer_name}"

class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('productos.Producto', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def subtotal(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.nombre} x{self.quantity}"

from cloudinary.models import CloudinaryField

class TelegramChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User Message'),
        ('admin', 'Admin Reply'),
    ]

    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    message = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)  # Store image in Cloudinary
    image_url = models.URLField(blank=True, null=True)  # URL to image in Cloudinary or other
    timestamp = models.DateTimeField(auto_now_add=True)
    telegram_message_id = models.CharField(max_length=100, blank=True)  # ID of message in Telegram
    replied = models.BooleanField(default=False)  # Whether admin replied in Telegram
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='user')
    # For admin replies, link to the original user message
    original_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='admin_replies')
    # Track which admin user sent the reply
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_replies')

    def __str__(self):
        sender = self.sender_name or 'Anonymous'
        if self.message_type == 'admin':
            sender = f"Admin ({self.admin_user.username if self.admin_user else 'Unknown'})"
        return f"{self.get_message_type_display()} from {sender} at {self.timestamp}"
