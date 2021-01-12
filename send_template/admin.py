from django.contrib import admin
from send_template.models import SendTemplate


@admin.register(SendTemplate)
class SendTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'channel', 'type', 'content', 'is_removed', 'created',
                    'modified']
    list_filter = ['is_removed', 'channel']
    filter_horizontal = ['ds']
    search_fields = ['name', 'content']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['name', 'ds', 'channel', 'type']}),
        ('管理信息', {'classes': ['grp-collapse grp-open'], 'fields': ['content']}),
        ('标记删除', {'classes': ['grp-collapse grp-open'], 'fields': ['is_removed']}),
    ]
