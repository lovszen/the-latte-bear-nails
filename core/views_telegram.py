from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Budget
from .serializers import BudgetTelegramCreateSerializer
from .utils import enviar_a_telegram


class BudgetCreateView(generics.CreateAPIView):
    queryset = Budget.objects.all()
    serializer_class = BudgetTelegramCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        instance = serializer.save(
            user=user,
            customer_name=user.get_full_name() or user.username,
            customer_email=user.email
        )
        mensaje = (
            f"📩 Nuevo presupuesto recibido\n\n"
            f"Título: {instance.title}\n"
            f"Cliente: {instance.customer_name}\n"
            f"Email: {instance.customer_email}\n"
            f"Total: ${instance.total_amount}"
        )
        enviar_a_telegram(mensaje)