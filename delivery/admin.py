from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from delivery.models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'name', 'owner', 'project', 'delay', 'is_removed', 'created',
                    'modified']
    list_display_links = ['indented_title']
    list_filter = ['is_removed', 'project', 'owner', 'upgrade_status']
    search_fields = ['name', 'owner__username', 'project__name']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['name', 'owner', 'project', 'delay', 'upgrade_status']}),
        ('管理信息', {'classes': ['grp-collapse grp-open'], 'fields': ['parent', 'group', 'receivers']}),
        ('标记删除', {'classes': ['grp-collapse grp-open'], 'fields': ['is_removed']}),
    ]
    mptt_level_indent = 20
    filter_horizontal = ['group', 'receivers']
