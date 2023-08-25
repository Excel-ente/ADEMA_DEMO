from django import forms

from producto.models import Producto, Categoria


class ProductoForm(forms.ModelForm):
    nombre = forms.TextInput(attrs={'class': 'form-control'})
    descripcion = forms.TextInput(attrs={'class': 'form-control'})
    precio = forms.DecimalField(initial=00.00, min_value=0,
                                widget=forms.NumberInput(attrs={
                                    'class': 'form-control',
                                }))
    precio_usd = forms.DecimalField(initial=00.00, min_value=0,
                                widget=forms.NumberInput(attrs={
                                    'class': 'form-control',
                                }))
    precio_bs = forms.DecimalField(initial=00.00, min_value=0,
                                widget=forms.NumberInput(attrs={
                                    'class': 'form-control',
                                }))

    categoria = forms.Select(attrs={'class': 'form-control'})

    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio','precio_usd', 'precio_bs', 'categoria']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del producto'
            }),
            'descripcion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Caja x 24 Unid.. Etc'
            }),
            'categoria':forms.Select(attrs={
                'class': 'form-control'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Envase',
            'precio': 'Precio en Pesos',
            'precio_usd': 'Precio en Dolares',
            'precio_bs': 'Precio en Bolivianos',
            'categoria': 'Categoría',
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la categoría'
            }),
        }
