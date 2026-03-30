import factory
from apps.cart.models import Cart, CartItem
from apps.users.factories import BuyerFactory


class CartFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Cart

    buyer  = factory.SubFactory(BuyerFactory)
    status = 'open'


class CartItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CartItem

    cart     = factory.SubFactory(CartFactory)
    product  = None  # set explicitly in tests once ProductFactory exists
    quantity = 1