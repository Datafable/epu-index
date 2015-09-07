from datetime import datetime

from django.core.management.base import BaseCommand

from epu_index.models import EpuIndexScore, JournalsScraped, Article, ARTICLES_APU_CUTOFF


class Command(BaseCommand):
    help = 'Calculate the daily EPU score for the given date and store the result to the EpuIndexScore\
            model/table.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('date', help="YYYY-MM-DD")

    def handle(self, *args, **options):
        day = datetime.strptime(options['date'], "%Y-%m-%d").date()

        self.stdout.write("Calculate EPU score for {d}...".format(d=day))

        number_of_journals = JournalsScraped.objects.filter(date=day).count()
        number_of_positive_articles = Article.objects.filter(published_at__year=day.year,
                                                             published_at__month=day.month,
                                                             published_at__day=day.day,
                                                             epu_score__gte=ARTICLES_APU_CUTOFF).count()

        if number_of_journals > 0:
            self.stdout.write("Number of journals scraped: {nj}".format(nj=number_of_journals))
            self.stdout.write("Number of articles above {cutoff}: {na}".format(cutoff=ARTICLES_APU_CUTOFF,
                                                                               na=number_of_positive_articles))

            day_epu_score = number_of_positive_articles / float(number_of_journals)
            self.stdout.write("Calculated EPU: {score}".format(score=day_epu_score))

            # Let's create or update EpuIndexScore
            new_values = {'number_of_articles': number_of_positive_articles,
                          'number_of_papers': number_of_journals,
                          'epu': day_epu_score}

            EpuIndexScore.objects.update_or_create(date=day, defaults=new_values)

        else:
            self.stdout.write("Nothing was scraped that day.")
