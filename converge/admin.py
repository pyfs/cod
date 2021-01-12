from django.contrib import admin
from converge.models import BurrConverge, DateTimeConverge, TimeConverge


# Register your models here.


@admin.register(BurrConverge)
class BurrConvergeAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'section', 'count', 'project', 'status', 'created', 'modified', 'is_removed']
    list_filter = ['status', 'is_removed']
    search_fields = ['name', 'project__name']
    fieldsets = [
        ('基本信息', {
            'classes': ['grp-collapse grp-open'],
            'fields': ['name', 'owner', 'section', 'count', 'project']
        }),
        ('状态管理', {'classes': ['grp-collapse grp-open'], 'fields': ['status', 'is_removed']}),
    ]


@admin.register(DateTimeConverge)
class DateTimeConvergeAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'reason', 'project', 'status', 'start', 'end', 'created', 'modified', 'is_removed']
    list_filter = ['status', 'is_removed']
    search_fields = ['name', 'project__name']
    fieldsets = [
        ('基本信息', {
            'classes': ['grp-collapse grp-open'],
            'fields': ['name', 'owner', 'reason', 'project', 'description']
        }),
        ('时间管理', {'classes': ['grp-collapse grp-open'], 'fields': ['start', 'end']}),
        ('状态管理', {'classes': ['grp-collapse grp-open'], 'fields': ['status', 'is_removed']}),
    ]


@admin.register(TimeConverge)
class TimeConvergeAdmin(admin.ModelAdmin):
    list_display = ['owner', 'start', 'end', 'status', 'created', 'modified', 'is_removed']
    list_filter = ['status', 'is_removed']
    search_fields = ['owner__username']
    fieldsets = [
        ('基本信息', {
            'classes': ['grp-collapse grp-open'],
            'fields': ['owner']
        }),
        ('时间管理', {'classes': ['grp-collapse grp-open'], 'fields': ['start', 'end']}),
        ('状态管理', {'classes': ['grp-collapse grp-open'], 'fields': ['status', 'is_removed']}),
    ]
