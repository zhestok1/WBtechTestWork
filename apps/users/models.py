from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    
    balance = models.DecimalField(verbose_name='Баланс', 
                                  max_digits=15, 
                                  decimal_places=2, 
                                  default=0.00, 
                                  validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['date_joined']
        
    def __str__(self):
        return f'{self.username}'

    
    