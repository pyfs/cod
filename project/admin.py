from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin
from project.models import Project


@admin.register(Project)
class ProjectAdmin(DraggableMPTTAdmin):
    list_display = ['tree_actions', 'indented_title', 'name', 'label', 'pic', 'owner', 'is_removed', 'created',
                    'modified']
    list_display_links = ['indented_title']
    list_filter = ['is_removed', 'pic', 'owner']
    search_fields = ['name', 'pic__username', 'owner__username', 'label']
    fieldsets = [
        ('基本信息',
         {'classes': ['grp-collapse grp-open'], 'fields': ['name', 'label', 'pic', 'filter_types', 'owner', 'parent']}),
        ('配置管理', {'classes': ['grp-collapse grp-open'], 'fields': ['converge_status']}),
        ('成员管理', {'classes': ['grp-collapse grp-open'], 'fields': ['members', 'subscribers']}),
        ('标签管理', {'classes': ['grp-collapse grp-open'], 'fields': ['tags']}),
        ('标记删除', {'classes': ['grp-collapse grp-open'], 'fields': ['is_removed']}),
    ]
    mptt_level_indent = 20
    filter_horizontal = ['members', 'subscribers']
