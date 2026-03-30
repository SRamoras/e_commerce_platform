import factory
from decimal import Decimal
from apps.orders.models import Order, OrderItem, OrderStatus
from apps.users.factories import BuyerFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    buyer        = factory.SubFactory(BuyerFactory)
    status       = OrderStatus.PENDING
    total_amount = Decimal('0.00')


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order      = factory.SubFactory(OrderFactory)
    product    = None  # set explicitly in tests once ProductFactory exists
    quantity   = 1
    unit_price = Decimal('9.99')