from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import F, Sum


class Cart(models.Model):
    class Status(models.TextChoices):
        OPEN   = 'open',   'Open'
        CLOSED = 'closed', 'Closed'

    buyer      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    status     = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f'Cart #{self.id} ({self.status}) - {self.buyer.username}'

    @property
    def subtotal(self):
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )
        return result['total'] or Decimal('0.00')


class CartItem(models.Model):
    cart       = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product    = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantity   = models.PositiveIntegerField(default=1)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('cart', 'product')]
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return f'{self.quantity}x {self.product.name} in Cart #{self.cart.id}'

    @property
    def subtotal(self):
        return self.quantity * self.product.price