from django.contrib import admin
from .models import UserProfile, User
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'phone_number', 'city', 'birth_date')
    search_fields = ('user__username', 'email')

admin.site.register(UserProfile, UserProfileAdmin)