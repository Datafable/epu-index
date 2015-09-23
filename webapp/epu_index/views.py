import datetime

from collections import Counter

from django.db.models.functions import Coalesce

from rest_framework.decorators import api_view, permission_classes

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings

from rest_framework_csv import renderers as r

from .models import EpuIndexScore, Article, WordsPerDay
from .serializers import EpuSerializer


def _param_to_date(string):
            """ Takes a YYYY-MM-DD string and return a Date object."""
            return datetime.datetime.strptime(string, '%Y-%m-%d').date()


def _filterdates_epu_queryset(start_date, end_date):

    queryset = EpuIndexScore.objects.all().order_by('date')

    # Optional filtering by start/end date.
    # Params are named 'start' and 'end' and use YYYY-MM-DD format.
    # Filters are inclusive (<= / >=)
    if start_date is not None:
        queryset = queryset.filter(date__gte=_param_to_date(start_date))

    if end_date is not None:
        queryset = queryset.filter(date__lte=_param_to_date(end_date))

    return queryset


# See API discussion/description in #8.
@api_view()
@permission_classes((AllowAny, ))
def term_frequency(request):
    start_date_s = request.GET.get('start_date', None)
    end_date_s = request.GET.get('end_date', None)
    max_words = int(request.GET.get('max_words', 50))

    if start_date_s:
        start_date = _param_to_date(start_date_s)
    else:
        # Apparently, no data before 1994
        start_date = _param_to_date('1990-01-01')

    if end_date_s:
        end_date = _param_to_date(end_date_s)
    else:
        end_date = datetime.date.today() + datetime.timedelta(days=2)

    cnt = Counter()

    d = start_date
    delta = datetime.timedelta(days=1)
    while d <= end_date:
        wpd = WordsPerDay.objects.filter(date=d)

        for w in wpd:
            # Skip numbers
            try:
                int(w.word)
            except ValueError:
                if len(w.word) > 1:  # Also skip one-letter words
                    cnt[w.word] += w.frequency

        d += delta

    most_common_words = cnt.most_common(max_words)

    # Transform result to the required format:
    r = [{"word": x[0], "count": x[1]} for x in most_common_words]

    return Response(r)


@api_view()
@permission_classes((AllowAny, ))
def highest_ranking_article(request):
    date_string = request.GET.get('date', None)
    if date_string is None:
        raise serializers.ValidationError('The date parameter is mandatory.')
    else:
        d = _param_to_date(date_string)
        d_min = datetime.datetime.combine(d, datetime.time.min)
        d_max = datetime.datetime.combine(d, datetime.time.max)

        # EPU null is considered to be 0 for this ranking.
        article = Article.positive_objects.annotate(epu_score_without_null=Coalesce('epu_score', 0))\
                                          .filter(published_at__range=(d_min, d_max))\
                                          .order_by('-epu_score_without_null').first()

        if article:
            return Response({'article_title': article.title,
                             'article_url': article.url,
                             'epu': article.epu_score,
                             'article_newspaper': article.news_journal.name})
        else:
            # Following Peter's requirements: empty array if no results for that day
            return Response([])


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
    # TODO: shouldn't this be removed since we provide get_queryset?
    queryset = EpuIndexScore.objects.all()
    serializer_class = EpuSerializer

    renderer_classes = [r.CSVRenderer] + api_settings.DEFAULT_RENDERER_CLASSES

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        return _filterdates_epu_queryset(start_date, end_date)
