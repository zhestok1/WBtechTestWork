from django.db import transaction
from rest_framework.exceptions import ValidationError
from apps.orders.models import Order, OrderItem
import logging

logger = logging.getLogger(__name__)

def create_order_from_cart(user):
    cart = getattr(user, 'cart', None)
    if not cart or not cart.cart_items.exists():
        raise ValidationError({"error": "Корзина пуста"})

    with transaction.atomic():
        total_price = 0
        items_to_create = []

        # 1. Проверяем остатки и считаем общую сумму
        for cart_item in cart.cart_items.select_related('product'):
            product = cart_item.product
            if product.stock < cart_item.quantity:
                raise ValidationError({"error": f"Товара '{product.name}' недостаточно на складе"})
            
            total_price += product.price * cart_item.quantity
            items_to_create.append((product, cart_item.quantity))

        # 2. Проверяем баланс пользователя
        if user.balance < total_price:
            raise ValidationError({"error": "Недостаточно средств на балансе"})

        # 3. Списываем баланс
        user.balance -= total_price
        user.save(update_fields=['balance'])

        # 4. Создаем заказ
        order = Order.objects.create(user=user, total_price=total_price)

        # 5. Списываем со склада и создаем позиции заказа
        for product, quantity in items_to_create:
            product.stock -= quantity
            product.save(update_fields=['stock'])

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )

        # 6. Очищаем корзину
        cart.cart_items.all().delete()

        logger.info(f"Заказ №{order.id} успешно создан для пользователя {user.email}")
        return order