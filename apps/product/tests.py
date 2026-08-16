from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.product.models import Product

User = get_user_model()


class ProductTests(APITestCase):

    def setUp(self):
        self.list_url = reverse('product_list')
        
        # Исправлено имя переменной на regular_user
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="Password123!"
        )

        self.admin_user = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="AdminPassword123!"
        )

        self.product = Product.objects.create(
            name="Тестовый смартфон",
            description="Отличный мощный смартфон",
            price=Decimal("49999.00"),
            stock=10
        )
        
        self.detail_url = reverse('product_item', kwargs={'pk': self.product.id})

        self.new_product_data = {
            "name": "Ноутбук",
            "description": "Рабочий ноутбук",
            "price": "89999.00",
            "stock": 5
        }

    def test_get_product_detail_allow_any(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)

    def test_create_product_by_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(self.list_url, self.new_product_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)

    def test_create_product_by_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(self.list_url, self.new_product_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)

    def test_create_product_unauthorized_forbidden(self):
        response = self.client.post(self.list_url, self.new_product_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_update_product_by_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(self.detail_url, {
            "price": "55000.00"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.price, Decimal("55000.00"))

    def test_update_product_by_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.patch(self.detail_url, {
            "price": "10.00"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_product_by_admin_success(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)

    def test_delete_product_by_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.delete(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Product.objects.count(), 1)