import pytest
from apps.orders.models import OrderStatus
from apps.orders.factories import OrderFactory


@pytest.mark.django_db
class TestOrderModel:
    def test_str(self, buyer):
        order = OrderFactory(buyer=buyer)
        assert str(order) == f'Order #{order.id} (pending) - {buyer.username}'

    def test_valid_transition_pending_to_confirmed(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.PENDING)
        order.transition_status(OrderStatus.CONFIRMED)
        assert order.status == OrderStatus.CONFIRMED

    def test_valid_transition_pending_to_cancelled(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.PENDING)
        order.transition_status(OrderStatus.CANCELLED)
        assert order.status == OrderStatus.CANCELLED

    def test_invalid_transition_confirmed_to_cancelled(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.CONFIRMED)
        with pytest.raises(ValueError):
            order.transition_status(OrderStatus.CANCELLED)

    def test_can_cancel_within_window(self, buyer):
        order = OrderFactory(buyer=buyer, status=OrderStatus.PENDING)
        assert order.can_cancel() is True