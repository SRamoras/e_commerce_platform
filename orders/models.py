from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone


class OrderStatus(models.TextChoices):
    PENDING   = 'pending',   'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    CANCELLED = 'cancelled', 'Cancelled'


class Order(models.Model):
    buyer        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status       = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_at   = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order #{self.id} ({self.status}) - {self.buyer.username}'

    def transition_status(self, new_status):
        valid = {
            OrderStatus.PENDING: [OrderStatus.CONFIRMED, OrderStatus.CANCELLED],
        }
        allowed = valid.get(self.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition from '{self.status}' to '{new_status}'."
            )
        self.status = new_status
        self.save()

    def can_cancel(self):
        delta = timezone.now() - self.created_at
        return self.status == OrderStatus.PENDING and delta.total_seconds() <= 1800

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    class FulfilmentStatus(models.TextChoices):
        UNFULFILLED = 'unfulfilled', 'Unfulfilled'
        FULFILLED   = 'fulfilled',   'Fulfilled'

    order             = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product           = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity          = models.PositiveIntegerField()
    unit_price        = models.DecimalField(max_digits=10, decimal_places=2)
    fulfilment_status = models.CharField(
        max_length=20,
        choices=FulfilmentStatus.choices,
        default=FulfilmentStatus.UNFULFILLED,
    )

    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'

    def __str__(self):
        return f'{self.quantity}x {self.product.name} (Order #{self.order.id})'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity