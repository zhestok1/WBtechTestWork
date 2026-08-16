from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from apps.product.models import Product


class CartAPIView(APIView):
    """
    Эндпоинт для работы с корзиной целиком:
    - GET /api/cart/ — посмотреть свою корзину (создается автоматически)
    - DELETE /api/cart/ — полностью очистить корзину
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.cart_items.all().delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemListAPIView(APIView):
    """
    Эндпоинт для добавления товаров в корзину:
    - POST /api/cart/items/ — добавить товар
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        product_id = serializer.validated_data['product_id']
        quantity = request.data.get('quantity', 1)
        
        product = get_object_or_404(Product, id=product_id)

        if product.stock < int(quantity):
            return Response({"error": "Недостаточно товара на складе"}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += int(quantity)
            if product.stock < cart_item.quantity:
                return Response({"error": "Превышен доступный остаток товара на складе"}, status=status.HTTP_400_BAD_REQUEST)
            cart_item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)


class CartItemDetailAPIView(APIView):
    """
    Эндпоинт для управления конкретной позицией в корзине:
    - PATCH /api/cart/items/{id}/ — изменить количество товара
    - DELETE /api/cart/items/{id}/ — удалить позицию из корзины
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return get_object_or_404(CartItem, id=pk, cart=cart)

    def patch(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        quantity = request.data.get('quantity')

        if quantity is not None:
            quantity = int(quantity)
            if quantity <= 0:
                cart_item.delete()
                return Response(CartSerializer(cart_item.cart).data, status=status.HTTP_200_OK)
            
            if cart_item.product.stock < quantity:
                return Response({"error": "Недостаточно товара на складе"}, status=status.HTTP_400_BAD_REQUEST)
            
            cart_item.quantity = quantity
            cart_item.save()

        return Response(CartSerializer(cart_item.cart).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        cart_item = self.get_object(pk, request.user)
        cart = cart_item.cart
        cart_item.delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)