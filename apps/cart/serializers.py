from rest_framework import serializers

from apps.product.serializers import ProductSerializer
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, source='get_total_price', read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'total_price']
        
class CartSerializer(serializers.ModelSerializer):
    
    items = CartItemSerializer(source='cart_items', many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'updated_at']

    def get_total_price(self, obj):
        return obj.get_total_price()