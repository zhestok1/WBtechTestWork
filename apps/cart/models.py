from django.db import models
from django.contrib.auth import get_user_model
from apps.product.models import Product

User = get_user_model()

class Cart(models.Model):
    
    user = models.OneToOneField(  
        User,
        verbose_name='Владелец корзины',
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания корзины',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Время последнего обновления корзины',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f'Корзина пользователя {self.user.username}'
    
    def get_total_price(self):
        """Общая стоимость всех товаров в корзине"""
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        verbose_name='Корзина',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    product = models.ForeignKey(
        Product,
        verbose_name='Товар',
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1  
    )
    added_at = models.DateTimeField(auto_now_add=True)  
    
    class Meta:
        verbose_name = 'Позиция корзины'
        verbose_name_plural = 'Позиции корзины'
        unique_together = ['cart', 'product']  
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def get_total_price(self):  
        return self.product.price * self.quantity