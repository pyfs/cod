from rest_framework import serializers

from silence.models import Silence


class UpdateOrCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Silence
        fields = ['project', 'type']
