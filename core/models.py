from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    customer_email = models.EmailField()
    customer_name = models.CharField(max_length=200)
    imagen_referencia = CloudinaryField('imagen_referencia', blank=True, null=True)

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

class PersonalizedRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personalized_requests')
    
    forma = models.CharField(max_length=50)
    largo = models.IntegerField()
    medidas = models.CharField(max_length=50)
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente de Cotización'),
        ('quoted', 'Presupuestado'),
        ('rejected', 'Rechazado'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    related_budget = models.OneToOneField(
        'Budget', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='original_request'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud Personalizada de {self.user.username} - {self.forma} ({self.status})"

class TelegramChatMessage(models.Model):
    MESSAGE_TYPE_CHOICES = [
        ('user', 'User Message'),
        ('admin', 'Admin Reply'),
    ]

    sender_name = models.CharField(max_length=100, blank=True)
    sender_email = models.EmailField(blank=True)
    message = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    telegram_message_id = models.CharField(max_length=100, blank=True)
    replied = models.BooleanField(default=False)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPE_CHOICES, default='user')
    original_message = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='admin_replies')
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_replies')

    def __str__(self):
        sender = self.sender_name or 'Anonymous'
        if self.message_type == 'admin':
            sender = f"Admin ({self.admin_user.username if self.admin_user else 'Unknown'})"
        return f"{self.get_message_type_display()} from {sender} at {self.timestamp}"