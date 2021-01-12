from django.contrib import admin
from auth_token.models import AuthToken


# Register your models here.


@admin.register(AuthToken)
class AuthTokenAdmin(admin.ModelAdmin):

    def is_effective(self, obj):
        """检测 token 生效"""
        return obj.is_expired

    list_display = ['name', 'token', 'owner', 'data_source', 'status', 'is_removed', 'start', 'end']
    list_filter = ['status']
    search_fields = ['name', 'token', 'owner_username', 'data_source__name']
    is_effective.short_description = '是否生效'
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['name', 'token', 'data_source', 'owner']}),
        ('时间管理', {'classes': ['grp-collapse grp-open'], 'fields': ['start', 'end']}),
        ('状态管理', {'classes': ['grp-collapse grp-open'], 'fields': ['status', 'is_removed']}),
    ]
