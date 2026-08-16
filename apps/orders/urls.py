from django.urls import path 
from .views import OrderCreateAPIView, OrderListAPIView

urlpatterns = [
    path('checkout/', OrderCreateAPIView.as_view(), name='checkout'),
    path('order_list/', OrderListAPIView.as_view(), name='order_list'),
]
