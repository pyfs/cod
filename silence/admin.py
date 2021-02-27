from django.contrib import admin
from silence.models import Silence


@admin.register(Silence)
class SilenceAdmin(admin.ModelAdmin):
    list_display = ['owner', 'project', 'ignore_type', 'event', 'start', 'end', 'modified']
    list_filter = ['project', 'ignore_type', 'owner', 'event']
    search_fields = ['owner__username', 'project__name']
    fieldsets = [
        ('基本信息', {'classes': ['grp-collapse grp-open'], 'fields': ['project', 'owner']}),
        ('选择开关', {'classes': ['grp-collapse grp-open'], 'fields': ['ignore_type', 'event']}),
        ('管理信息', {'classes': ['grp-collapse grp-open'], 'fields': ['start', 'end']}),
    ]
