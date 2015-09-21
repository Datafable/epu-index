from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from epu_index.models import (Article, WordsPerDay, create_wordsperday_from_articles,
                              ARTICLES_APU_CUTOFF)


class Command(BaseCommand):
    help = 'Calculate the word frequency for the All articles in database and store the result to\
            the WordsPerDay model/table.'

    def handle(self, *args, **options):
        self.stdout.write("Calculate word frequency for all articles...")

        # First we have to truncate WordsPerDay
        self.stdout.write("Truncate previous data...")
        WordsPerDay.objects.all().delete()

        self.stdout.write("Calculate new word frequency. That may takes long.")

        # We use a paginator to avoid loading all articles into memory
        paginator = Paginator(Article.objects.filter(epu_score__gt=ARTICLES_APU_CUTOFF), 1000)

        for page in range(1, paginator.num_pages + 1):
            create_wordsperday_from_articles(paginator.page(page).object_list)
            self.stdout.write('.')
            self.stdout.flush()
