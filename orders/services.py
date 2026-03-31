from django.db import transaction
from django.utils import timezone

from products.services import decrement_stock, restore_stock
from cart.models import Cart
from .models import Order, OrderItem, OrderStatus


def checkout(user):
    cart = (
        Cart.objects.filter(buyer=user, status=Cart.Status.OPEN)
        .prefetch_related("items__variant__product")
        .first()
    )

    if not cart or not cart.items.exists():
        raise ValueError("Cart is empty")

    with transaction.atomic():
        order = Order.objects.create(
            buyer=user,
            status=OrderStatus.PENDING,
            total_amount=0,
        )

        order_items = []
        for cart_item in cart.items.all():
            variant = cart_item.variant

            decrement_stock(variant.id, cart_item.quantity, user=user)

            order_items.append(
                OrderItem(
                    order=order,
                    variant=variant,
                    quantity=cart_item.quantity,
                    unit_price=variant.price,
                )
            )

        OrderItem.objects.bulk_create(order_items)

        order.total_amount = order.total
        order.save()

        cart.status = Cart.Status.CLOSED
        cart.save()

    return order


def confirm_order(user, order_id):
    order = Order.objects.get(pk=order_id, buyer=user)

    if order.status != OrderStatus.PENDING:
        raise ValueError(f"Cannot confirm order with status {order.status}")

    order.transition_status(OrderStatus.CONFIRMED)
    return order


def cancel_order(user, order_id):
    order = Order.objects.prefetch_related("items__variant").get(
        pk=order_id, buyer=user
    )

    if order.status != OrderStatus.PENDING:
        raise ValueError(f"Cannot cancel order with status {order.status}")

    time_diff = timezone.now() - order.created_at
    if time_diff.total_seconds() > 30 * 60:
        raise ValueError("Cancellation window (30 minutes) has expired")

    with transaction.atomic():
        for item in order.items.all():
            restore_stock(item.variant.id, item.quantity, user=user)

        order.transition_status(OrderStatus.CANCELLED)

    return order


def fulfil_item(seller, order_id, item_id):
    order = Order.objects.prefetch_related("items__variant__product").get(pk=order_id)

    item = order.items.get(pk=item_id)

    if item.variant.product.seller != seller:
        raise ValueError("You can only fulfil items from your own products")

    item.fulfilment_status = "fulfilled"
    item.save()

    return item


def get_seller_orders(seller):
    from products.models import Product
    from django.db.models import Q

    orders = (
        Order.objects.filter(items__variant__product__seller=seller)
        .distinct()
        .prefetch_related("items__variant__product", "buyer")
        .order_by("-created_at")
    )

    return orders


def get_order_summary(seller, start_date=None, end_date=None):
    from django.db.models import Count, Sum
    from django.db.models.functions import TruncDate
    from products.models import Product

    queryset = Order.objects.filter(items__variant__product__seller=seller).exclude(
        status=OrderStatus.CANCELLED
    )

    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)

    summary = (
        queryset.annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(
            order_count=Count("id"),
            total_revenue=Sum("total_amount"),
        )
        .order_by("-date")
    )

    return list(summary)
