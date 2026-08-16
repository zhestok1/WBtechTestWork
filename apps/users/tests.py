from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.cart.models import Cart

User = get_user_model()


class UsersTests(APITestCase):
    
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.profile_url = reverse('profile')
        self.balance_url = reverse('balance')
        
        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "MyPass1303",
            "password_confirm": "MyPass1303"
        }
        
        self.user = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="Password123!",
            balance=Decimal("100.00")
        )
        
        Cart.objects.get_or_create(user=self.user)
        
    def test_user_register(self):
        response = self.client.post(
            self.register_url, self.user_data, format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        
        new_user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(Cart.objects.filter(user=new_user).exists())
        
    def test_user_login(self):
        response = self.client.post(
            self.login_url, 
            {
                'username': self.user.username,
                'password': 'Password123!'
            },
            format='json'
        )   
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_user_logout(self):
        refresh = RefreshToken.for_user(user=self.user)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        response = self.client.post(
            self.logout_url, 
            {'refresh_token': str(refresh)},
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        
        response_reuse = self.client.post(
            self.logout_url, 
            {"refresh_token": str(refresh)}, 
            format='json'
        )
        self.assertEqual(response_reuse.status_code, status.HTTP_400_BAD_REQUEST)  
        
    def test_get_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        
    def test_update_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(self.profile_url, {
            "email": "newemail@example.com"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "newemail@example.com")
        
    def test_get_balance(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.balance_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '100.00')
        
    def test_top_up_balance_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.balance_url, {
            "amount": "50.50"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['new_balance'], "150.50")
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("150.50"))
        
    def test_top_up_balance_invalid_amount(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.balance_url, {
            "amount": "-10.00"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("100.00"))

    def test_top_up_balance_string(self):
       
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.balance_url, {
            "amount": "abc"
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, Decimal("100.00"))

    def test_login_missing_fields(self):
      
        response = self.client.post(self.login_url, {
            "username": self.user.username
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_register_without_email(self):

        data = self.user_data.copy()
        data.pop('email')
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)