from rest_framework import serializers

from apps.users.serializers import UserSerializer
from .models import Order, OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'product', 'price', 'quantity')
        
class OrderSerializer(serializers.ModelSerializer):
    
    items = OrderItemSerializer(many=True, source='order_items', read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order 
        fields = ('id', 'user', 'items', 'total_price', 'status', 'created_at', 'updated_at')
        read_only_fields = ('created_at', 'updated_at')
    