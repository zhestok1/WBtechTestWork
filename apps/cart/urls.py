from django.urls import path
from .views import CartAPIView, CartItemListAPIView, CartItemDetailAPIView

urlpatterns = [
    
    path('cart/', CartAPIView.as_view(), name='cart-detail'),
    
    path('cart/items/', CartItemListAPIView.as_view(), name='cart-item-list'),
    
    path('cart/items/<int:pk>/', CartItemDetailAPIView.as_view(), name='cart-item-detail'),
]
    
