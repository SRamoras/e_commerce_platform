from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ["added_at"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "buyer", "status", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["buyer__username", "buyer__email"]
    inlines = [CartItemInline]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["id", "cart", "variant", "quantity", "added_at"]
    list_filter = ["quantity"]
    search_fields = ["cart__id", "variant__name"]
