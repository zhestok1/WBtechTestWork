from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)
    fields = ('product', 'price', 'quantity', 'get_total_price')
    can_delete = False
    
    def get_total_price(self, obj):
        return obj.get_total_price
    get_total_price.short_description = 'Сумма позиции'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'id')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'status', 'total_price')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['confirm_orders', 'ship_orders', 'deliver_orders', 'cancel_orders']
    
    def confirm_orders(self, request, queryset):
        queryset.update(status=Order.Status.CONFIRMED)
    confirm_orders.short_description = 'Подтвердить выбранные заказы'
    
    def ship_orders(self, request, queryset):
        queryset.update(status=Order.Status.SHIPPED)
    ship_orders.short_description = 'Отправить выбранные заказы'
    
    def deliver_orders(self, request, queryset):
        queryset.update(status=Order.Status.DELIVERED)
    deliver_orders.short_description = 'Доставить выбранные заказы'
    
    def cancel_orders(self, request, queryset):
        queryset.update(status=Order.Status.CANCELLED)
    cancel_orders.short_description = 'Отменить выбранные заказы'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'price', 'quantity', 'get_total_price')
    list_filter = ('order__status',)
    search_fields = ('order__user__username', 'product__name')
    readonly_fields = ('price',)
    
    def get_total_price(self, obj):
        return obj.get_total_price
    get_total_price.short_description = 'Сумма позиции'
    
