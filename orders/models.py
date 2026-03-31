from django.db import models
from django.conf import settings
from products.models import ProductVariant


class OrderStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"


class Order(models.Model):
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    status = models.CharField(
        max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id} ({self.status}) - {self.buyer.username}"

    def transition_status(self, new_status):
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
            OrderStatus.CONFIRMED: [],
            OrderStatus.CANCELLED: [],
        }
        if new_status not in valid_transitions.get(self.status, []):
            raise ValueError(f"Invalid transition from {self.status} to {new_status}")
        self.status = new_status
        self.save()

    @property
    def total(self):
        from django.db.models import Sum, F

        result = self.items.aggregate(total=Sum(F("quantity") * F("unit_price")))
        return result["total"] or 0


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    fulfilment_status = models.CharField(
        max_length=20,
        choices=[
            ("unfulfilled", "Unfulfilled"),
            ("fulfilled", "Fulfilled"),
        ],
        default="unfulfilled",
    )

    def __str__(self):
        return f"{self.variant.product.name} - {self.variant.name} x{self.quantity}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
