from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

from apps.cart.models import Cart
from .serializers import UserRegistrationSerializer, UserSerializer


User = get_user_model()

class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save()
        Cart.objects.get_or_create(user=user)
        return user


class LoginView(TokenObtainPairView):
    pass


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {"error": "Поле 'refresh_token' обязательно."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response(  
                {"message": "Вы успешно вышли из системы."},
                status=status.HTTP_205_RESET_CONTENT
            )
            
        except TokenError:
            return Response(
                {"error": "Токен недействителен или уже просрочен."},
                status=status.HTTP_400_BAD_REQUEST
            )


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)  
        serializer.save()
        return Response(serializer.data)


class BalanceView(APIView):
    """Пополнение баланса"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        return Response({
            'balance': str(request.user.balance)
        })
    
    def post(self, request):
        amount = request.data.get('amount')
        
        if not amount:
            return Response(
                {"error": "Необходимо указать сумму пополнения"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            return Response(
                {"error": "Сумма должна быть положительным числом"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user
        user.balance += amount
        user.save(update_fields=['balance'])
        
        return Response({
            "message": f"Баланс пополнен на {amount:.2f} руб.",
            "new_balance": str(user.balance)
        })