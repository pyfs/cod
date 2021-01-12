from django.contrib import admin
from receive_strategy.models import ReceiveStrategy


@admin.register(ReceiveStrategy)
class ReceiveStrategyAdmin(admin.ModelAdmin):
    list_display = ['owner', 'channel', 'created', 'start', 'end', 'modified', 'is_removed']
    list_filter = ['is_removed', 'owner', 'channel']
    search_fields = ['owner__username', 'channel']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['owner']}),
        ('管理信息', {'classes': ['grp-collapse grp-open'], 'fields': ['channel', 'start', 'end']}),
        ('标记删除', {'classes': ['grp-collapse grp-open'], 'fields': ['is_removed']}),
    ]
