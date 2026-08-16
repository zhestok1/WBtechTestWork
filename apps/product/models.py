from django.core.validators import MinValueValidator
from django.db import models

class Product(models.Model):
    
    name = models.CharField(
        verbose_name='Имя товара', 
        max_length=300, 
        blank=False
    )
    
    description = models.TextField(
        verbose_name='Описание товара',
        blank=True, null=True
    )
    
    price = models.DecimalField(
        verbose_name='Цена товара',
        max_digits=30, 
        decimal_places=2, 
        validators=[MinValueValidator(0)],
        blank=False
    )
    
    stock = models.BigIntegerField(
        verbose_name='Количество товара на складе', 
        default=0, 
        blank=False,
        validators=[MinValueValidator(0)]
    )
    
    created_at = models.DateTimeField(
        verbose_name='Дата создания товара',
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления товара', 
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        
    def __str__(self):
        return f'{self.name} - {self.price} руб.'
    