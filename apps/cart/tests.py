from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.product.models import Product
from apps.cart.models import Cart, CartItem

User = get_user_model()


class CartTests(APITestCase):

    def setUp(self):
        # Очищаем базу перед каждым тестом
        Product.objects.all().delete()
        Cart.objects.all().delete()

        # Создаем пользователя
        self.user = User.objects.create_user(
            username="cartuser",
            email="cartuser@example.com",
            password="Password123!"
        )

        self.product = Product.objects.create(
            name="Игровой ноутбук",
            description="Мощный ноутбук",
            price=Decimal("100000.00"),
            stock=5
        )

        
        self.cart_url = reverse('cart-detail')          
        self.cart_items_url = reverse('cart-item-list') 

        self.client.force_authenticate(user=self.user)

    def test_get_empty_cart(self):
        """Тест: просмотр корзины (если она пустая, она должна автоматически создаваться)"""
        response = self.client.get(self.cart_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['items']), 0)
        self.assertEqual(response.data['total_price'], 0) 

    def test_add_item_to_cart_success(self):
        """Тест: успешное добавление товара в корзину"""
        data = {
            "product_id": self.product.id,
            "quantity": 2
        }
        response = self.client.post(self.cart_items_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 2)
        self.assertEqual(response.data['total_price'], Decimal("200000.00"))

    def test_add_item_exceeds_stock(self):
   
        data = {
            "product_id": self.product.id,
            "quantity": 10  # На складе всего 5
        }
        response = self.client.post(self.cart_items_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)

    def test_update_cart_item_quantity(self):
        """Тест: изменение количества товара в корзине (PATCH)"""
        # Сначала добавляем товар
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        detail_url = reverse('cart-item-detail', kwargs={'pk': cart_item.id})
        
        response = self.client.patch(detail_url, {"quantity": 3}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)

    def test_delete_cart_item(self):
        
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(cart=cart, product=self.product, quantity=1)
        
        detail_url = reverse('cart-item-detail', kwargs={'pk': cart_item.id})
        
        response = self.client.delete(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.count(), 0)

    def test_clear_entire_cart(self):
        
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        
        response = self.client.delete(self.cart_url)
        
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        self.assertEqual(cart.cart_items.count(), 0)