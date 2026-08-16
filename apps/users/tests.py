from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationTest(TestCase):
    """Тесты регистрации пользователя"""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!'
        }
    
    def test_register_success(self):
        """Успешная регистрация"""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        self.assertTrue(User.objects.first().check_password('StrongPass123!'))
    
    def test_register_with_existing_username(self):
        """Регистрация с существующим username"""
        User.objects.create_user(username='testuser', password='pass123')
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
    
    def test_register_password_mismatch(self):
        """Несовпадение паролей"""
        data = self.valid_data.copy()
        data['password_confirm'] = 'DifferentPass123!'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
    
    def test_register_weak_password(self):
        """Слабый пароль"""
        data = self.valid_data.copy()
        data['password'] = '123'
        data['password_confirm'] = '123'
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_without_email(self):
        """Регистрация без email"""
        data = self.valid_data.copy()
        data.pop('email')
        response = self.client.post(self.register_url, data)
        # email может быть пустым, но должен быть валидный
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.first().email, '')


class UserLoginTest(TestCase):
    """Тесты авторизации"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!'
        )
        self.valid_credentials = {
            'username': 'testuser',
            'password': 'StrongPass123!'
        }
    
    def test_login_success(self):
        """Успешный вход"""
        response = self.client.post(self.login_url, self.valid_credentials)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_login_wrong_password(self):
        """Неверный пароль"""
        data = {'username': 'testuser', 'password': 'WrongPass123!'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        """Несуществующий пользователь"""
        data = {'username': 'nonexistent', 'password': 'pass123'}
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_fields(self):
        """Отсутствуют поля"""
        response = self.client.post(self.login_url, {'username': 'testuser'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserProfileTest(TestCase):
    """Тесты профиля"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPass123!',
            balance=100.50
        )
        self.profile_url = reverse('profile')
        
        # Получаем токен
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_profile_success(self):
        """Получение профиля"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['balance'], '100.50')
    
    def test_get_profile_unauthenticated(self):
        """Профиль без токена"""
        self.client.credentials()  # Убираем токен
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_update_profile_success(self):
        """Обновление профиля"""
        data = {'email': 'newemail@example.com'}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
    
    def test_update_profile_username(self):
        """Обновление username"""
        data = {'username': 'newusername'}
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')


class UserBalanceTest(TestCase):
    """Тесты баланса"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='StrongPass123!',
            balance=100.00
        )
        self.balance_url = reverse('balance')
        
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_get_balance_success(self):
        """Получение баланса"""
        response = self.client.get(self.balance_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['balance'], '100.00')
    
    def test_get_balance_unauthenticated(self):
        """Баланс без токена"""
        self.client.credentials()
        response = self.client.get(self.balance_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_top_up_balance_success(self):
        """Пополнение баланса"""
        data = {'amount': 50.50}
        response = self.client.post(self.balance_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 150.50)
        self.assertEqual(response.data['new_balance'], '150.50')
    
    def test_top_up_balance_zero(self):
        """Пополнение на 0"""
        data = {'amount': 0}
        response = self.client.post(self.balance_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 100.00)  # Не изменился
    
    def test_top_up_balance_negative(self):
        """Пополнение на отрицательную сумму"""
        data = {'amount': -50}
        response = self.client.post(self.balance_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertEqual(self.user.balance, 100.00)
    
    def test_top_up_balance_string(self):
        """Пополнение строкой"""
        data = {'amount': 'abc'}
        response = self.client.post(self.balance_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_top_up_balance_missing_amount(self):
        """Отсутствует сумма"""
        response = self.client.post(self.balance_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLogoutTest(TestCase):
    """Тесты выхода"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='StrongPass123!'
        )
        self.logout_url = reverse('logout')
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_logout_success(self):
        """Успешный выход"""
        data = {'refresh_token': str(self.refresh)}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
    
    def test_logout_without_refresh_token(self):
        """Выход без refresh токена"""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_logout_with_invalid_refresh_token(self):
        """Выход с невалидным токеном"""
        data = {'refresh_token': 'invalid_token'}
        response = self.client.post(self.logout_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_logout_unauthenticated(self):
        """Выход без токена"""
        self.client.credentials()
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)