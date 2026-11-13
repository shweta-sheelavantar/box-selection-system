from django.contrib import admin
from .models import Box, Product, Order, OrderItem


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('name', 'length', 'width', 'height', 'max_weight', 'cost')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'length', 'width', 'height', 'weight')
    search_fields = ('name',)


class OrderItemInline(admin.TabularInline):
    """
    Inline editor for OrderItems inside the Order admin page.
    Lets you add products + quantities directly on the order form.
    """
    model = OrderItem
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'total_weight', 'recommended_box', 'created_at')
    list_filter = ('recommended_box',)
    readonly_fields = ('created_at', 'total_weight', 'recommended_box', 'reasoning')
    inlines = [OrderItemInline]
