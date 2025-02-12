from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Profile, ShippingAddress

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ("first_name", "last_name", "email", "unique_id", "is_staff", "is_active", "last_login", "date_joined")
    list_filter = ("email", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'unique_id')}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    search_fields = ("email", "first_name", "last_name", "unique_id")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions",)
    
    # Make unique_id read-only in admin
    readonly_fields = ("id", "unique_id", "last_login", "date_joined",)

    def save_model(self, request, obj, form, change):
        """Ensure unique_id is generated before saving"""
        if not obj.unique_id:
            obj.unique_id = obj.generate_unique_id()
        obj.save()

admin.site.register(CustomUser, CustomUserAdmin)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'unique_id', 'phone', 'address1', 'address2', 'city', 'state', 'zipcode', 'country', 'old_cart')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

    def unique_id(self, obj):
        """Return the unique_id from the associated CustomUser."""
        return obj.user.unique_id
    unique_id.admin_order_field = 'user__unique_id'  # Allows sorting by unique_id
    unique_id.short_description = 'Unique ID'

admin.site.register(Profile, ProfileAdmin)

class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'full_name', 'email', 'address1', 'address2', 'city', 'state', 'zipcode', 'country')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')

admin.site.register(ShippingAddress, ShippingAddressAdmin)
