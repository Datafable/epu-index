from .models import EpuIndexScore
from rest_framework import serializers


class EpuSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EpuIndexScore
        fields = ('date', 'epu')
