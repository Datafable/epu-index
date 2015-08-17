import datetime

from collections import Counter

from django.db.models.functions import Coalesce

from rest_framework.decorators import api_view, permission_classes

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.settings import api_settings

from rest_framework_csv import renderers as r

from .models import EpuIndexScore, Article
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

# TO TEST:
# - That only positive EPU articles are checked.
# - That the default values works for the 3 parameters 
# - That the stopwords are avoided
# - That all is converted to lowercase
# - That the results are correct (form and format)

# TO DOCUMENT IN TICKET:
# - endpoint URL
# - default parameters

# See API discussion/description in #8.
@api_view()
@permission_classes((AllowAny, ))
def term_frequency(request):
    start_date = request.GET.get('start_date', None)
    end_date = request.GET.get('end_date', None)
    max_words = int(request.GET.get('max_words', 50))

    # We start with only an article with positive EPU...
    articles = Article.objects.filter(epu_score__gt=0)

    # ...if start_date is provided, we refine...
    if start_date:
        d = _param_to_date(start_date)
        d_min = datetime.datetime.combine(d, datetime.time.min)
        articles = articles.filter(published_at__gte=d_min)

    # ... if end_date is provided, we refine further ...
    if end_date:
        d = _param_to_date(end_date)
        d_max = datetime.datetime.combine(d, datetime.time.max)
        articles = articles.filter(published_at__lte=d_max)

    cnt = Counter()

    for a in articles:
        words = a.cleaned_text_without_stopwords().split()
        for w in words:
            cnt[w] += 1

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
        article = Article.objects.annotate(epu_score_without_null=Coalesce('epu_score', 0))\
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
    queryset = EpuIndexScore.objects.all()  # TODO: shouldn't this be removed since we provide get_queryset?
    serializer_class = EpuSerializer

    renderer_classes = [r.CSVRenderer] + api_settings.DEFAULT_RENDERER_CLASSES

    def get_queryset(self):
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        return _filterdates_epu_queryset(start_date, end_date)
