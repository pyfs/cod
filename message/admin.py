from django.contrib import admin
from message.models import Message


# Register your models here.

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['project', 'data_source', 'host', 'type', 'title', 'level', 'status', 'created', 'modified']
    list_filter = ['status', 'project', 'data_source', 'host', 'type', 'level']
    search_fields = ['project', 'data_source', 'host', 'type', 'title', 'extra']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['project', 'host', 'type', 'title']}),
        ('状态管理', {'classes': ['grp-collapse grp-open'], 'fields': ['status', 'level']}),
        ('原始数据', {'classes': ['grp-collapse grp-open'], 'fields': ['extra']}),
    ]
