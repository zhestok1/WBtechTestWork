from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.product.models import Product
from apps.cart.models import Cart, CartItem
from apps.orders.models import Order, OrderItem

User = get_user_model()


class OrderTests(APITestCase):

    def setUp(self):
        # Очищаем базу перед каждым тестом
        Product.objects.all().delete()
        Cart.objects.all().delete()
        Order.objects.all().delete()

        # Создаем пользователя с балансом 
        self.user = User.objects.create_user(
            username="orderuser",
            email="orderuser@example.com",
            password="Password123!",
            balance=Decimal("150000.00")  # Начальный баланс
        )

        # Создаем тестовый продукт 
        self.product = Product.objects.create(
            name="Смартфон",
            price=Decimal("50000.00"),
            stock=5
        )

        # Создаем корзину и добавляем товар
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )

       
        self.order_list_url = reverse('order_list')      
        self.checkout_url = reverse('checkout')    

        # Аутентификация
        self.client.force_authenticate(user=self.user)

    def test_checkout_success(self):
        """Тест: успешное создание заказа из корзины (Checkout)"""
        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.total_price, Decimal("100000.00"))  # 50000 * 2
        self.assertEqual(order.order_items.count(), 1)

        # Проверяем, что баланс пользователя уменьшился (150000 - 100000 = 50000)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("50000.00"))

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # Проверяем, что корзина очищена
        self.assertEqual(self.cart.cart_items.count(), 0)

    def test_checkout_empty_cart(self):
        """Тест: ошибка при попытке заказать из пустой корзины"""
        self.cart.cart_items.all().delete()  # Очищаем корзину

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_insufficient_stock(self):
        """Тест: ошибка, если товара на складе меньше, чем в корзине"""
        self.product.stock = 1 
        self.product.save()

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_checkout_insufficient_balance(self):
        """Тест: ошибка, если у пользователя недостаточно средств на балансе"""
        self.user.balance = Decimal("1000.00")  # Заказ стоит 100000, а баланс 1000
        self.user.save()

        response = self.client.post(self.checkout_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(Order.objects.count(), 0)

    def test_get_order_list(self):
        """Тест: просмотр списка заказов пользователя"""
        # Сначала создаем заказ через оформление
        self.client.post(self.checkout_url)

        response = self.client.get(self.order_list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['total_price'], "100000.00")
        self.assertEqual(len(response.data[0]['items']), 1)