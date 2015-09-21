from datetime import datetime

from django.core.management.base import BaseCommand

from epu_index.models import (Article, create_wordsperday_from_articles, remove_all_wordsperday_day,
                              ARTICLES_APU_CUTOFF)


class Command(BaseCommand):
    help = 'Calculate the word frequency for the given date and store the result to the WordsPerDay\
            model/table.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('date', help="YYYY-MM-DD")

    def handle(self, *args, **options):
        day = datetime.strptime(options['date'], "%Y-%m-%d").date()

        self.stdout.write("Calculate word frequency for {d}...".format(d=day))

        # We only take into account article with positive EPU
        articles = Article.objects.filter(published_at__year=day.year,
                                          published_at__month=day.month,
                                          published_at__day=day.day,
                                          epu_score__gt=ARTICLES_APU_CUTOFF)

        # First we have to remove all previous entries for that day!
        remove_all_wordsperday_day(day)
        create_wordsperday_from_articles(articles)
