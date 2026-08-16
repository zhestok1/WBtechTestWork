from django.urls import path
from .views import ProductView

urlpatterns = [
    path('', ProductView.as_view({'get': 'list', 'post': 'create'}), name='product_list'),
    path('<int:pk>/', ProductView.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='product_item'),
    
]