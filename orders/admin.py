from django.contrib import admin
from apps.orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ['product', 'quantity', 'unit_price', 'fulfilment_status']
    can_delete      = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ['id', 'buyer', 'status', 'total_amount', 'created_at']
    list_filter     = ['status']
    readonly_fields = ['total_amount', 'created_at']
    inlines         = [OrderItemInline]
    search_fields   = ['buyer__username']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ['id', 'order', 'product', 'quantity', 'unit_price', 'fulfilment_status']
    list_filter   = ['fulfilment_status']
    readonly_fields = ['order', 'product', 'quantity', 'unit_price', 'fulfilment_status']