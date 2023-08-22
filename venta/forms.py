from django import forms
from .models import MONEDAS
from agenda.models import Cliente,Vendedor
from venta.models import Venta

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = {'razon_cancelacion', }
        widgets = {
            'razon_cancelacion': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'true',
                'placeholder': 'Escriba una razón detallada'
            })
        }
        labels = {
            'razon_cancelacion': 'Razón'
        }


class VentaFacturaForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(queryset=Cliente.objects.all(), empty_label="Seleccionar cliente", widget=forms.Select(attrs={
        'class': 'form-control',
        'required': True,
    }))
    vendedor = forms.ModelChoiceField(queryset=Vendedor.objects.all(), empty_label="Seleccionar Vendedor", widget=forms.Select(attrs={
        'class': 'form-control',
        'required': True,
    }))

    moneda = forms.ChoiceField(
        choices=[
            ('Pesos', 'Pesos'),
            ('Dolares', 'Dolares'),
            ('Bolivianos', 'Bolivianos'),
        ],
        widget=forms.Select
    )

    class Meta:
        model = Venta
        fields = ['vendedor', 'cliente',]
    

    def save(self, commit=True):
        venta = super().save(commit=False)
        cliente = self.cleaned_data['cliente']
        vendedor = self.cleaned_data['vendedor']
        vendedor = self.cleaned_data['vendedor']
        venta.cliente = cliente
        venta.vendedor = vendedor
        venta.facturar(cliente=cliente, vendedor=vendedor)  # Pasamos directamente los objetos cliente y vendedor.
        if commit:
            venta.save()
        return venta