from datetime import timedelta

from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from event.models import Event
from project.models import Project
from silence.models import Silence
from silence.serializer import UpdateOrCreateSerializer
from utils.drf.filters import OwnerFilter


class SilenceViewSet(ModelViewSet):
    queryset = Silence.objects.all()
    serializer_class = UpdateOrCreateSerializer
    filter_backends = [OwnerFilter]

    @staticmethod
    def get_time_frame(time):
        """根据事件间隔获取起始和结束时间"""
        return now(), now() + timedelta(hours=time)

    @action(methods=['POST'], detail=False)
    def update_or_create(self, request, *args, **kwargs):
        project = Project.objects.get(id=request.data['project'])
        event = Event.objects.get(id=request.data['type'])
        start, end = self.get_time_frame(time=request.data['time'])
        instance, created = Silence.objects.update_or_create(project=project,
                                                             type=event,
                                                             owner=request.user,
                                                             defaults={
                                                                 "start": start,
                                                                 "end": end
                                                             })
        if created:
            message = "创建沉默规则成功"
        else:
            message = "更新沉默规则成功"

        return Response({"status": 'success', 'message': message}, status=status.HTTP_200_OK)
