from django.urls import path
from apps.orders import views

app_name = 'orders'

urlpatterns = [
    path('',                                        views.order_list_view,      name='list'),
    path('checkout/',                               views.checkout_view,        name='checkout'),
    path('summary/',                                views.order_summary_view,   name='summary'),
    path('seller/',                                 views.seller_orders_view,   name='seller-orders'),
    path('<int:pk>/',                               views.order_detail_view,    name='detail'),
    path('<int:pk>/confirm/',                       views.confirm_order_view,   name='confirm'),
    path('<int:pk>/cancel/',                        views.cancel_order_view,    name='cancel'),
    path('<int:pk>/items/<int:item_id>/fulfil/',    views.seller_fulfil_view,   name='seller-fulfil'),
]