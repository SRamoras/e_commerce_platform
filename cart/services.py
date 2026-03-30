from django.shortcuts import get_object_or_404
from apps.cart.models import Cart, CartItem


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(buyer=user, status='open')
    return cart


def add_to_cart(user, product_id, quantity):
    from apps.products.models import Product
    product = get_object_or_404(Product, pk=product_id, is_active=True)

    if product.stock < quantity:
        raise ValueError(f'Only {product.stock} units available.')

    cart = get_or_create_cart(user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        new_qty = item.quantity + quantity
        if product.stock < new_qty:
            raise ValueError(f'Only {product.stock} units available.')
        item.quantity = new_qty
        item.save()

    return item


def remove_from_cart(user, item_id):
    cart = get_or_create_cart(user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()


def update_cart_item(user, item_id, quantity):
    from apps.products.models import Product
    cart = get_or_create_cart(user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)

    if item.product.stock < quantity:
        raise ValueError(f'Only {item.product.stock} units available.')

    item.quantity = quantity
    item.save()
    return item


def clear_cart(user):
    cart = get_or_create_cart(user)
    cart.items.all().delete()


def get_cart_contents(user):
    cart = get_or_create_cart(user)
    items = cart.items.select_related('product').all()
    return {
        'cart_id': cart.id,
        'status': cart.status,
        'subtotal': str(cart.subtotal),
        'items': [
            {
                'item_id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'price': str(item.product.price),
                'quantity': item.quantity,
                'subtotal': str(item.subtotal),
                'in_stock': item.product.stock >= item.quantity,
            }
            for item in items
        ],
    }