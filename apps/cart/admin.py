from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline): 
    model = CartItem
    extra = 0
    readonly_fields = ('added_at',)
    fields = ('product', 'quantity', 'added_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    ordering = ('-updated_at',)
    
    def total_price(self, obj):
        return obj.get_total_price()
    total_price.short_description = 'Общая сумма корзины'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'cart', 'product', 'quantity', 'get_total_price', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('cart__user__username', 'product__name')
    readonly_fields = ('added_at',)
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Сумма позиции'