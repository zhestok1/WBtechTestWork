from django.db import models
from django.contrib.auth import get_user_model
from apps.product.models import Product
from django.core.validators import MinValueValidator

User = get_user_model()

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'В обработке'
        CONFIRMED = 'confirmed', 'Подтверждён'
        SHIPPED = 'shipped', 'Отправлен'
        DELIVERED = 'delivered', 'Доставлен'
        CANCELLED = 'cancelled', 'Отменён'
    
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        related_name='orders' 
    )
    total_price = models.DecimalField(
        verbose_name='Общая сумма заказа',
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        verbose_name='Статус заказа',
        max_length=20, 
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания заказа',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления заказа',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at'] 
    
    def __str__(self):
        return f'Заказ #{self.id} - {self.user.username}' 


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='Заказ',
        related_name='order_items'  
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='order_items' 
    )
    price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Цена на момент заказа' 
    )
    quantity = models.PositiveIntegerField(
        verbose_name='Количество',
        default=1
    )
    
    class Meta:
        verbose_name = 'Позиция заказа'  
        verbose_name_plural = 'Позиции заказа' 
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity} = {self.get_total_price}'
    
    @property
    def get_total_price(self):
        return self.price * self.quantity