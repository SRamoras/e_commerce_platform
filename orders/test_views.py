import pytest
from django.test import Client
from apps.orders.factories import OrderFactory
from apps.orders.models import OrderStatus


@pytest.mark.django_db
class TestOrderViews:
    def test_list_requires_auth(self):
        client = Client()
        response = client.get('/api/orders/')
        assert response.status_code == 401

    def test_seller_cannot_list_orders(self, seller):
        client = Client()
        client.force_login(seller)
        response = client.get('/api/orders/')
        assert response.status_code == 403

    def test_buyer_gets_own_orders(self, buyer):
        OrderFactory(buyer=buyer)
        client = Client()
        client.force_login(buyer)
        response = client.get('/api/orders/')
        assert response.status_code == 200
        assert response.json()['success'] is True

    def test_buyer_cannot_see_other_buyers_order(self, buyer, buyer_b):
        order = OrderFactory(buyer=buyer_b)
        client = Client()
        client.force_login(buyer)
        response = client.get(f'/api/orders/{order.id}/')
        assert response.status_code == 404

    def test_checkout_empty_cart_returns_400(self, buyer):
        client = Client()
        client.force_login(buyer)
        response = client.post('/api/orders/checkout/')
        assert response.status_code == 400