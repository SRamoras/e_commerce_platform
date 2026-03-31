from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        "variant",
        "quantity",
        "unit_price",
        "subtotal",
        "fulfilment_status",
    ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "buyer", "status", "total_amount", "created_at", "updated_at"]
    list_filter = ["status"]
    search_fields = ["buyer__username", "buyer__email"]
    readonly_fields = ["total_amount", "created_at", "updated_at"]
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "order",
        "variant",
        "quantity",
        "unit_price",
        "subtotal",
        "fulfilment_status",
    ]
    list_filter = ["fulfilment_status"]
    search_fields = ["order__id", "variant__name"]
    readonly_fields = ["order", "variant", "quantity", "unit_price", "subtotal"]
