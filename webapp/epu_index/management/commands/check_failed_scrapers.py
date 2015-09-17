from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail

from epu_index.models import NewsJournal, Article

from django.conf import settings


class Command(BaseCommand):
    help = 'Load CSV file to populate NewsJournal model.'

    def handle(self, *args, **options):
        consecutive_days = settings.CONSECUTIVE_DAYS_WITHOUT_ARTICLES

        scrapers = NewsJournal.objects.all()

        start_time = timezone.now() - timezone.timedelta(days=consecutive_days)

        for scraper in scrapers:
            n = Article.objects.filter(news_journal=scraper, published_at__gte=start_time).count()
            if n == 0:
                print 'spider {s} failed'.format(s=scraper.spider_name)
                msg = ("Spider {s} failed for {n} consecutive days. Please check if this is a "
                       "normal situation or if a spider failed.").format(s=scraper.spider_name,
                                                                         n=consecutive_days)

                send_mail(settings.ALERT_EMAIL_SUBJECT,
                          msg,
                          settings.ALERT_EMAIL_FROM,
                          settings.ALERT_EMAIL_TO)
