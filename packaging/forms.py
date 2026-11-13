from django import forms
from .models import Product


class OrderItemForm(forms.Form):
    """
    One row in the order formset: pick a product and enter a quantity.
    Uses a ModelChoiceField so the dropdown is populated from the database.
    """
    product = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Product',
        empty_label='Select a product…',
    )
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Qty',
        }),
        label='Quantity',
    )

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        # If a product is selected, quantity must also be provided
        if product and not quantity:
            self.add_error('quantity', 'Enter a quantity for this product.')
        return cleaned_data
