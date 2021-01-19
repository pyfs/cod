from django.contrib import admin
from event.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'host', 'level', 'current_delivery', 'converge', 'status', 'is_removed', 'created', 'modified']
    list_filter = ['status', 'is_removed', 'project', 'host', 'level']
    search_fields = ['name', 'project__name', 'host', 'type']
    filter_horizontal = ['messages', 'receivers']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['name', 'project', 'host', 'level', 'current_delivery', 'converge', 'extra']}),
        ('人员管理', {'classes': ['grp-collapse grp-open'], 'fields': ['receivers']}),
        ('标签管理', {'classes': ['grp-collapse grp-open'], 'fields': ['tags']}),
        ('标记删除', {'classes': ['grp-collapse grp-open'], 'fields': ['is_removed']}),
    ]
