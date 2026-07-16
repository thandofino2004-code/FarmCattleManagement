from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile

# Unregister default User admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'is_staff', 'is_active', 'is_approved']
    list_filter = ['is_staff', 'is_active']
    search_fields = ['username', 'email']
    
    def is_approved(self, obj):
        return obj.profile.is_approved
    is_approved.boolean = True
    is_approved.short_description = "Approved?"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_approved', 'phone_number']
    list_editable = ['is_approved']
    search_fields = ['user__username', 'user__email']
