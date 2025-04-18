from django import forms
from django.forms import modelformset_factory
from compras.models import Compra, DetalleCompra

class CompraForm(forms.ModelForm):
    class Meta:
        model = Compra
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full p-2 border border-gray-300 rounded-md text-xs',
            })

DetalleCompraFormSet = modelformset_factory(
    DetalleCompra,
    fields=('producto', 'cantidad', 'precio_unitario', 'igv', 'observacion'),
    extra=1,
    can_delete=True
)
