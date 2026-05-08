"""Admin registrations for common application."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

User = get_user_model()


admin.site.site_header = 'CRM Administration'
admin.site.site_title = 'CRM Admin'
admin.site.index_title = 'Administration'


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Extended user admin with convenient group and permission controls."""

    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_login',
    )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'groups',
    )
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    filter_horizontal = (
        'groups',
        'user_permissions',
    )


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    """Extended group admin for predefined CRM roles."""

    search_fields = ('name',)
    filter_horizontal = ('permissions',)
