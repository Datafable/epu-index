from rest_framework import viewsets

from .models import EpuIndexScore
from .serializers import EpuSerializer


class EpuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EpuIndexScore.objects.all()
    serializer_class = EpuSerializer
