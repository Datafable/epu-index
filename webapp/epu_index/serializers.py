from .models import EpuIndexScore
from rest_framework import serializers


class EpuSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EpuIndexScore
        fields = ('date', 'epu', 'number_of_newspapers', 'number_of_articles')
