from django.db import models


class Box(models.Model):
    """
    Represents a shipping box available in inventory.
    Dimensions are in centimetres, max_weight in kg, cost in currency units.
    """
    name = models.CharField(max_length=100)
    length = models.DecimalField(max_digits=7, decimal_places=2)
    width = models.DecimalField(max_digits=7, decimal_places=2)
    height = models.DecimalField(max_digits=7, decimal_places=2)
    max_weight = models.DecimalField(max_digits=7, decimal_places=2)
    cost = models.DecimalField(max_digits=8, decimal_places=2)

    def volume(self):
        return self.length * self.width * self.height

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.length}×{self.width}×{self.height} cm, "
            f"max {self.max_weight} kg, ₹{self.cost})"
        )

    class Meta:
        ordering = ['cost']          # cheapest first — matches selection logic
        verbose_name_plural = 'boxes'


class Product(models.Model):
    """
    Represents a product that can be added to an order.
    Dimensions are in centimetres, weight in kg.
    """
    name = models.CharField(max_length=200)
    length = models.DecimalField(max_digits=7, decimal_places=2)
    width = models.DecimalField(max_digits=7, decimal_places=2)
    height = models.DecimalField(max_digits=7, decimal_places=2)
    weight = models.DecimalField(max_digits=7, decimal_places=2)

    def volume(self):
        return self.length * self.width * self.height

    def __str__(self):
        return (
            f"{self.name} "
            f"({self.length}×{self.width}×{self.height} cm, {self.weight} kg)"
        )

    class Meta:
        ordering = ['name']


class Order(models.Model):
    """
    Represents a customer order containing one or more products.
    After the box selection algorithm runs, recommended_box, total_weight,
    and reasoning are populated and saved.
    """
    created_at = models.DateTimeField(auto_now_add=True)

    # Many-to-many through OrderItem so we can store quantity per product
    products = models.ManyToManyField(Product, through='OrderItem')

    # Fields filled in by the selection algorithm
    recommended_box = models.ForeignKey(
        Box,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='orders'
    )
    total_weight = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True
    )
    reasoning = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Order #{self.pk} — {self.created_at.strftime('%d %b %Y %H:%M')}"

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    """
    Intermediate table for the Order ↔ Product many-to-many relationship.
    Stores how many units of a product are in a given order.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def line_weight(self):
        """Weight contribution of this line: product weight × quantity."""
        return self.product.weight * self.quantity

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"

    class Meta:
        unique_together = ('order', 'product')
