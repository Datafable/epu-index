from django.core.management.base import BaseCommand

from epu_index.models import (Article, WordsPerDay, create_wordsperday_from_articles,
                              ARTICLES_APU_CUTOFF)


class Command(BaseCommand):
    help = 'Calculate the word frequency for the All articles in database and store the result to\
            the WordsPerDay model/table.'

    def handle(self, *args, **options):
        self.stdout.write("Calculate word frequency for all articles...")

        # Only EPU positive articles are taken into account:
        articles = Article.objects.filter(epu_score__gt=ARTICLES_APU_CUTOFF)

        # First we have to truncate WordsPerDay
        WordsPerDay.objects.all().delete()
        create_wordsperday_from_articles(articles)
