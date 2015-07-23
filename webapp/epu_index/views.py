from datetime import datetime

from rest_framework.decorators import api_view, permission_classes

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings

from rest_framework_csv import renderers as r

from .models import EpuIndexScore
from .serializers import EpuSerializer


def _filterdates_epu_queryset(start_date, end_date):
    def _param_to_date(string):
            """ Takes a YYYY-MM-DD string and return a Date object."""
            return datetime.strptime(string, '%Y-%m-%d').date()

    queryset = EpuIndexScore.objects.all().order_by('date')

    # Optional filtering by start/end date.
    # Params are named 'start' and 'end' and use YYYY-MM-DD format.
    # Filters are inclusive (<= / >=)
    if start_date is not None:
        queryset = queryset.filter(date__gte=_param_to_date(start_date))

    if end_date is not None:
        queryset = queryset.filter(date__lte=_param_to_date(end_date))

    return queryset


@api_view()
@permission_classes((AllowAny, ))
def epu_per_month(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)

    queryset = _filterdates_epu_queryset(start_date, end_date)

    # 1. For each year-month pair, we keep the sum of EPUs and the number of involved days
    months = {}
    for e in queryset:
        key = "{year}-{month:0>2d}".format(year=e.date.year, month=e.date.month)
        if key in months:
            months[key]['total_epu'] += e.epu
            months[key]['days_count'] += 1
        else:
            months[key] = {'total_epu': e.epu, 'days_count': 1}

    # 2. Based on the sum and number of days, we compute an average per month:
    processed_months = {}
    for k, v in months.iteritems():
        processed_months[k] = v['total_epu'] / v['days_count']

    # 3. Results are in an object, we want an ordered array for API consistency (see ticket #39)
    results = []
    for k, v in processed_months.iteritems():
        results.append({'month': k, 'epu': v})

    results = sorted(results, key=lambda e: e['month'])

    return Response(results)


class EpuViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EpuIndexScore.objects.all()  # TODO: shouldn't this be removed since we provide get_queryset?
    serializer_class = EpuSerializer

    renderer_classes = [r.CSVRenderer] + api_settings.DEFAULT_RENDERER_CLASSES

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        return _filterdates_epu_queryset(start_date, end_date)
