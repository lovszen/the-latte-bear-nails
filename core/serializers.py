from rest_framework import serializers
from .models import Budget, BudgetItem, TelegramChatMessage
from productos.models import Producto


class BudgetItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.nombre', read_only=True)
    
    class Meta:
        model = BudgetItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'subtotal']


class BudgetSerializer(serializers.ModelSerializer):
    items = BudgetItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Budget
        fields = ['id', 'user', 'title', 'created_at', 'total_amount', 
                  'customer_email', 'customer_name', 'items']
        read_only_fields = ['id', 'created_at', 'total_amount', 'items']


class BudgetTelegramCreateSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(required=False, allow_blank=True)
    customer_email = serializers.EmailField(required=False, allow_blank=True)
    
    class Meta:
        model = Budget
        fields = ['title', 'customer_email', 'customer_name', 'total_amount']

    def create(self, validated_data):
        return super().create(validated_data)


class TelegramChatMessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(required=False, allow_blank=True)
    sender_email = serializers.EmailField(required=False, allow_blank=True)
    
    class Meta:
        model = TelegramChatMessage
        fields = ['id', 'sender_name', 'sender_email', 'message', 'image', 'image_url', 'timestamp', 'replied', 'message_type', 'original_message', 'admin_user']
        read_only_fields = ['id', 'timestamp', 'replied', 'message_type', 'original_message', 'admin_user']


class TelegramChatAdminReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramChatMessage
        fields = ['id', 'message', 'image', 'image_url', 'original_message', 'timestamp', 'message_type', 'admin_user']
        read_only_fields = ['id', 'timestamp', 'message_type', 'admin_user']

    def validate_original_message(self, value):
        """Ensure the original message exists and is not already replied to"""
        if value and value.message_type != 'user':
            raise serializers.ValidationError("Can only reply to user messages")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['admin_user'] = request.user
        validated_data['message_type'] = 'admin'
        return super().create(validated_data)