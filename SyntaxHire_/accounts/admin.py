from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'user_type', 'is_staff', 'is_active', 'created_at', 'updated_at')
    list_filter = ('user_type', 'is_staff', 'is_active')
    search_fields = ('email',)
    ordering = ('email',)