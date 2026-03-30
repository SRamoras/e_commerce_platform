from django.contrib import admin
from apps.cart.models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model  = CartItem
    extra  = 0
    fields = ['product', 'quantity', 'added_at']
    readonly_fields = ['added_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display   = ['id', 'buyer', 'status', 'created_at']
    list_filter    = ['status']
    search_fields  = ['buyer__username']
    inlines        = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display  = ['id', 'cart', 'product', 'quantity', 'added_at']
    search_fields = ['product__name']