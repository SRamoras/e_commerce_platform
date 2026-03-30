from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from apps.cart.models import Cart
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.products.services import decrement_stock, restock


def checkout(user):
    cart = Cart.objects.filter(buyer=user, status='open').first()
    if not cart:
        raise ValueError('No open cart found.')

    items = list(cart.items.select_related('product').all())
    if not items:
        raise ValueError('Cart is empty.')

    with transaction.atomic():
        order = Order.objects.create(buyer=user, status=OrderStatus.PENDING)

        order_items = []
        for cart_item in items:
            decrement_stock(cart_item.product.id, cart_item.quantity, user=user)
            order_items.append(OrderItem(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                unit_price=cart_item.product.price,
            ))

        OrderItem.objects.bulk_create(order_items)

        order.total_amount = sum(
            oi.unit_price * oi.quantity for oi in order_items
        )
        order.save()

        cart.status = 'closed'
        cart.save()

    return order


def confirm_order(user, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=user)
    order.transition_status(OrderStatus.CONFIRMED)
    return order


def cancel_order(user, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=user)

    if not order.can_cancel():
        raise ValueError(
            'Order cannot be cancelled. Either already confirmed/cancelled or the 30-minute window has passed.'
        )

    with transaction.atomic():
        for item in order.items.select_related('product').all():
            restock(item.product.id, item.quantity, user=user)
        order.transition_status(OrderStatus.CANCELLED)

    return order