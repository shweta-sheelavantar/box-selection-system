from django.shortcuts import render, redirect, get_object_or_404
from django.forms import formset_factory
from .forms import OrderItemForm
from .models import Order, OrderItem, Product, Box
from .services import run_selection_and_save


def home(request):
    """Landing page — shows the 5 most recent orders."""
    recent = Order.objects.select_related('recommended_box').prefetch_related('items__product')[:5]
    return render(request, 'packaging/home.html', {'recent': recent})


def create_order(request):
    """
    GET  — show a formset of product-quantity rows.
    POST — validate, create the Order + OrderItems, run selection, redirect.
    """
    OrderItemFormSet = formset_factory(OrderItemForm, extra=1)
    has_products = Product.objects.exists()

    if request.method == 'POST':
        formset = OrderItemFormSet(request.POST)
        if formset.is_valid():
            # Collect only rows where a product was actually selected
            filled_rows = [
                form.cleaned_data
                for form in formset
                if form.cleaned_data and form.cleaned_data.get('product')
            ]
            if not filled_rows:
                # Formset is structurally valid but no products chosen
                formset._non_form_errors = formset.error_class(
                    ['Please select at least one product.']
                )
            else:
                order = Order.objects.create()
                for cd in filled_rows:
                    OrderItem.objects.create(
                        order=order,
                        product=cd['product'],
                        quantity=cd['quantity'],
                    )
                run_selection_and_save(order)
                return redirect('order_result', pk=order.pk)
    else:
        formset = OrderItemFormSet()

    return render(request, 'packaging/create_order.html', {
        'formset': formset,
        'has_products': has_products,
        'boxes': Box.objects.all(),   # read-only, for the sidebar inventory card
    })


def order_result(request, pk):
    """Displays the recommendation result for a completed order."""
    order = get_object_or_404(
        Order.objects.select_related('recommended_box').prefetch_related('items__product'),
        pk=pk
    )
    return render(request, 'packaging/order_result.html', {'order': order})
