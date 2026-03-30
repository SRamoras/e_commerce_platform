import json
import pytest
from django.test import Client
from apps.cart.models import Cart


@pytest.mark.django_db
class TestCartView:
    def test_unauthenticated_returns_401(self):
        client = Client()
        response = client.get('/api/cart/')
        assert response.status_code == 401

    def test_seller_cannot_view_cart(self, seller):
        client = Client()
        client.force_login(seller)
        response = client.get('/api/cart/')
        assert response.status_code == 403

    def test_buyer_gets_empty_cart(self, buyer):
        client = Client()
        client.force_login(buyer)
        response = client.get('/api/cart/')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['items'] == []

    def test_add_requires_product_id(self, buyer):
        client = Client()
        client.force_login(buyer)
        response = client.post(
            '/api/cart/add/',
            data=json.dumps({'quantity': 1}),
            content_type='application/json',
        )
        assert response.status_code == 400

    def test_clear_cart(self, buyer):
        client = Client()
        client.force_login(buyer)
        Cart.objects.get_or_create(buyer=buyer, status='open')
        response = client.post('/api/cart/clear/')
        assert response.status_code == 200