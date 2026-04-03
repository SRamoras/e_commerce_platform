from django.db import models
from django.conf import settings
from products.models import ProductVariant


class Cart(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="carts",
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Cart #{self.id} ({self.status}) - {self.buyer.username}"

    @property
    def subtotal(self):
        from django.db.models import F, Sum

        result = self.items.aggregate(total=Sum(F("quantity") * F("variant__price")))
        return result["total"] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("cart", "variant")]

    def __str__(self):
        return f"{self.variant.product.name} - {self.variant.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.quantity * self.variant.price
