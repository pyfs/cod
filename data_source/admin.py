from django.contrib import admin
from data_source.models import DataSource


# Register your models here.


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'close_timeout', 'is_enabled', 'status', 'is_removed', 'created', 'modified']
    list_filter = ['is_removed', 'status']
    search_fields = ['name', 'label']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['name', 'label', 'close_timeout', 'is_enabled']}),
        ('状态管理', {'classes': ['grp-collapse grp-open'], 'fields': ['status', 'is_removed']}),
    ]
