import logging
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from apps.cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer

# Инициализируем логгер для текущего модуля
logger = logging.getLogger(__name__)


class OrderCreateAPIView(APIView):
   
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # 1. Получаем корзину пользователя
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            logger.warning(f"Пользователь {user.username} (ID: {user.id}) попытался оформить заказ с пустой корзиной (корзина не найдена).")
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        cart_items = cart.cart_items.select_related('product').all()
        if not cart_items.exists():
            logger.warning(f"Пользователь {user.username} (ID: {user.id}) попытался оформить заказ с пустой корзиной (нет товаров).")
            return Response({"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        # Используем транзакцию, чтобы все этапы выполнились атомарно
        with transaction.atomic():
            
            # 2. Проверка остатков на складе и расчет итоговой суммы
            total_price = 0
            for item in cart_items:
                if item.product.stock < item.quantity:
                    logger.info(f"Ошибка заказа: товар '{item.product.name}' (ID: {item.product.id}) закончился. На складе: {item.product.stock}, запрошено: {item.quantity}.")
                    return Response(
                        {"error": f"Товар '{item.product.name}' недоступен в нужном количестве. На складе: {item.product.stock}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                total_price += item.product.price * item.quantity

            # 3. Проверка баланса пользователя
            if hasattr(user, 'balance') and user.balance < total_price:
                logger.info(f"Ошибка заказа для пользователя {user.username}: недостаточно средств. Требуется: {total_price}, баланс: {user.balance}.")
                return Response(
                    {"error": f"Недостаточно средств на балансе. Требуется: {total_price}, доступно: {user.balance}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 4. Списание баланса
            if hasattr(user, 'balance'):
                user.balance -= total_price
                user.save()

            # 5. Создание заказа
            order = Order.objects.create(
                user=user,
                total_price=total_price,
                status=Order.Status.PENDING
            )

            # 6. Перенос позиций в заказ и списание со склада
            for item in cart_items:
                product = item.product
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=item.quantity
                )

                product.stock -= item.quantity
                product.save()

            # 7. Очистка корзины
            cart.cart_items.all().delete()

            # 8. Логирование успешного создания заказа
            logger.info(f"Заказ #{order.id} на сумму {total_price} успешно создан для пользователя {user.username} (ID: {user.id}).")

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related('order_items__product')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)