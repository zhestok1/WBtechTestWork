from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'balance', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Финансы', {'fields': ('balance',)}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Финансы', {'fields': ('balance',)}),
    )
    
    readonly_fields = ('date_joined', 'last_login')
