from django.db.models import Q
from model_utils.models import now
from rest_framework.filters import BaseFilterBackend


class ProjectFilterBackend(BaseFilterBackend):
    """根据用户关注的项目过滤事件"""

    def filter_queryset(self, request, queryset, view):
        current = request.user
        return queryset.filter(
            Q(project__in=current.subscribe_project.all()) | Q(project__in=current.belong_to_project.all()) | Q(
                project__in=current.charged_project.all()))


class OwnerFilter(BaseFilterBackend):
    """过滤属于当前用户的数据"""

    def filter_queryset(self, request, queryset, view):
        current = request.user
        return queryset.filter(owner=current)


class TimeRangeFilter(BaseFilterBackend):
    """时间区间过滤器"""

    def filter_queryset(self, request, queryset, view):
        return queryset.filter(
            Q(start__isnull=True) | Q(end__isnull=True) | Q(start__lte=now) | Q(end__gte=now)).filter(
            ~Q(start__gt=now)).filter(~Q(end__lt=now))
