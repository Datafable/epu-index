import csv

from django.http import StreamingHttpResponse
from django.db import models

from rest_framework import viewsets

from .models import EpuIndexScore
from .serializers import EpuSerializer


def epu_streaming_csv(request):
    # We use streaming to avoid issues with large datasets
    # Logic taken from http://aeguana.com/blog/csv-export-data-for-django-model/
    # TODO: code is a bit ugly, but that's not that easy to improve.
    epu_qs = EpuIndexScore.objects.all()

    model = epu_qs.model
    model_fields = model._meta.fields + model._meta.many_to_many
    headers = [field.name for field in model_fields]

    class Echo(object):
        """An object that implements just the write method of the file-like interface."""

        def write(self, value):
            """Write the value by returning it, instead of storing in a buffer."""
            return value

    def get_row(obj):
        row = []
        for field in model_fields:
            if type(field) == models.ForeignKey:
                val = getattr(obj, field.name)
                if val:
                    val = val.__unicode__()
            elif type(field) == models.ManyToManyField:
                val = u', '.join([item.__unicode__() for item in getattr(obj, field.name).all()])
            elif field.choices:
                val = getattr(obj, 'get_%s_display' % field.name)()
            else:
                val = getattr(obj, field.name)
            row.append(unicode(val).encode("utf-8"))
        return row

    def stream(headers, data):
        if headers:
            yield headers
        for obj in data:
            yield get_row(obj)

    pseudo_buffer = Echo()

    writer = csv.writer(pseudo_buffer)

    response = StreamingHttpResponse((writer.writerow(row) for row in stream(headers, epu_qs)),
                                     content_type="text/csv")

    response['Content-Disposition'] = 'attachment; filename="epu_index.csv"'

    return response


class EpuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EpuIndexScore.objects.all()
    serializer_class = EpuSerializer
