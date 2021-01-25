from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import User
from account.forms import UserChangeForm, UserCreationForm


# Register your models here.


@admin.register(User)
class AccountUserAdmin(UserAdmin):
    fieldsets = [
        ('必填字段', {'classes': ['grp-collapse grp-open'], 'fields': ('cn_name', 'email', 'mobile')}),
        ('选填字段', {'classes': ['grp-collapse grp-open'], 'fields': ('first_name', 'last_name', 'avatar')}),
        ('联系方式', {'classes': ['grp-collapse grp-open'], 'fields': ('wx', 'qq')}),
        ('群组权限', {'classes': ['grp-collapse grp-open'], 'fields': ('groups', 'user_permissions')}),
        ('用户设置', {'classes': ['grp-collapse grp-open'], 'fields': ('filter_types', 'global_immunity', 'similar_block', 'tags')}),
        ('用户权限', {
            'classes': ['grp-collapse grp-closed'],
            'fields': ['is_active', 'is_staff', 'is_superuser', 'is_removed']
        }),
        ('时间信息', {'classes': ['grp-collapse grp-open'], 'fields': ['last_login', 'date_joined']}),
    ]

    add_fieldsets = (
        ('用户信息', {
            'classes': ['grp-collapse grp-open'],
            'fields': ['username', 'cn_name', 'email', 'password', 'mobile']}),
    )
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = ['username', 'cn_name', 'email', 'mobile', 'wx', 'global_immunity', 'similar_block', 'is_active', 'is_superuser',
                    'is_removed']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'is_removed']
    search_fields = ['email', 'mobile', 'wx', 'username', 'cn_name']
    ordering = ['username']
