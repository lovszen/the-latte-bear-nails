from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('budget/create/', views.create_budget, name='create_budget'),
    path('budget/<int:budget_id>/', views.view_budget, name='view_budget'),
    path('budget/<int:budget_id>/edit/', views.edit_budget, name='edit_budget'),
    path('budget/<int:budget_id>/delete/', views.delete_budget, name='delete_budget'),
    path('budgets/', views.budgets_list, name='budgets_list'),
    path('budget/generate/', views.generate_and_send_budget, name='generate_budget'),
    path('budget/download/<int:budget_id>/', views.download_budget_pdf, name='download_budget'),
]