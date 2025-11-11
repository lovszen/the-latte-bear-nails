from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'forma', 'tamaño', 
                 'color_principal', 'color_secundario', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Press On Almendrado Rosa'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del producto...'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'forma': forms.Select(attrs={'class': 'form-select'}),
            'tamaño': forms.Select(attrs={'class': 'form-select'}),
            'color_principal': forms.Select(attrs={'class': 'form-select'}),
            'color_secundario': forms.Select(attrs={'class': 'form-select'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control'}),
        }