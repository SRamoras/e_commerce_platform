import json
from django.core.paginator import Paginator
from django.db.models import Sum, F
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from apps.users.decorators import buyer_required, seller_required
from apps.orders.models import Order, OrderItem
from apps.orders import services


def _serialize_order(order):
    return {
        'id': order.id,
        'status': order.status,
        'total_amount': str(order.total_amount),
        'created_at': order.created_at.isoformat(),
        'items': [
            {
                'item_id': item.id,
                'product_id': item.product_id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.unit_price),
                'subtotal': str(item.subtotal),
                'fulfilment_status': item.fulfilment_status,
            }
            for item in order.items.select_related('product').all()
        ],
    }


@csrf_exempt
@buyer_required
def checkout_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        order = services.checkout(request.user)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'success': True, 'data': _serialize_order(order)}, status=201)


@buyer_required
def order_detail_view(request, pk):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    order = get_object_or_404(Order, pk=pk, buyer=request.user)
    return JsonResponse({'success': True, 'data': _serialize_order(order)})


@buyer_required
def order_list_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    qs = Order.objects.filter(buyer=request.user)
    paginator = Paginator(qs, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return JsonResponse({
        'success': True,
        'data': [_serialize_order(o) for o in page],
        'page': page.number,
        'total_pages': paginator.num_pages,
    })


@csrf_exempt
@buyer_required
def confirm_order_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        order = services.confirm_order(request.user, pk)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'success': True, 'data': _serialize_order(order)})


@csrf_exempt
@buyer_required
def cancel_order_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        order = services.cancel_order(request.user, pk)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'success': True, 'data': _serialize_order(order)})


@seller_required
def seller_orders_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    orders = Order.objects.filter(
        items__product__seller=request.user
    ).distinct().prefetch_related('items__product')
    paginator = Paginator(orders, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return JsonResponse({
        'success': True,
        'data': [_serialize_order(o) for o in page],
        'page': page.number,
        'total_pages': paginator.num_pages,
    })


@csrf_exempt
@seller_required
def seller_fulfil_view(request, pk, item_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    item = get_object_or_404(
        OrderItem,
        pk=item_id,
        order_id=pk,
        product__seller=request.user,
    )
    item.fulfilment_status = OrderItem.FulfilmentStatus.FULFILLED
    item.save()
    return JsonResponse({'success': True, 'data': {'item_id': item.id, 'fulfilment_status': item.fulfilment_status}})


@seller_required
def order_summary_view(request):
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    date_from = request.GET.get('from')
    date_to   = request.GET.get('to')

    qs = OrderItem.objects.filter(product__seller=request.user)
    if date_from:
        qs = qs.filter(order__created_at__date__gte=date_from)
    if date_to:
        qs = qs.filter(order__created_at__date__lte=date_to)

    summary = (
        qs
        .annotate(date=TruncDate('order__created_at'))
        .values('date')
        .annotate(
            total_revenue=Sum(F('quantity') * F('unit_price')),
            total_items=Sum('quantity'),
        )
        .order_by('date')
    )

    return JsonResponse({'success': True, 'data': list(summary)})