import pytest
from decimal import Decimal
from apps.cart.factories import CartFactory, CartItemFactory


@pytest.mark.django_db
class TestCartModel:
    def test_str(self, buyer):
        cart = CartFactory(buyer=buyer)
        assert str(cart) == f'Cart #{cart.id} (open) - {buyer.username}'

    def test_subtotal_empty(self, buyer):
        cart = CartFactory(buyer=buyer)
        assert cart.subtotal == Decimal('0.00')

    def test_default_status_is_open(self, buyer):
        cart = CartFactory(buyer=buyer)
        assert cart.status == 'open'