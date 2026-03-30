import pytest
from django.test import Client
from apps.orders.models import OrderStatus
from apps.orders.services import cancel_order, confirm_order
from apps.orders.factories import OrderFactory


@pytest.mark.django_db
class TestOrderServices:
    def test_confirm_order(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.PENDING)
        confirmed = confirm_order(buyer, order.id)
        assert confirmed.status == OrderStatus.CONFIRMED

    def test_cancel_order_within_window(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.PENDING)
        cancelled = cancel_order(buyer, order.id)
        assert cancelled.status == OrderStatus.CANCELLED

    def test_cannot_cancel_confirmed_order(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.CONFIRMED)
        with pytest.raises(ValueError):
            cancel_order(buyer, order.id)