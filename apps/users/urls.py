from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from django.urls import path 
from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    BalanceView,
    ProfileView
)

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('balance/', BalanceView.as_view(), name='balance'), 
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
