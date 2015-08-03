import csv
import urllib2
import datetime

from django.core.management.base import BaseCommand
from epu_index.models import EpuIndexScore


# TODO: make it more versatile: delimiter, field order, date format, ...


class Command(BaseCommand):
    help = 'Load CSV file to populate EpuIndexScore models.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('csv_url')

        parser.add_argument('--truncate',
                            action='store_true',
                            dest='truncate',
                            default=False,
                            help='Truncate EPU data table before import.')

    def handle(self, *args, **options):
        csvfile = urllib2.urlopen(options['csv_url'])

        reader = csv.reader(csvfile, delimiter=';')

        # We truncate only after successfully opening the CSV file...
        if options['truncate']:
            self.stdout.write('Truncating EPU data table...')
            EpuIndexScore.objects.all().delete()

        iterrows = iter(reader)
        next(iterrows)

        for row in iterrows:
            d = datetime.datetime.strptime(row[0], "%d-%b-%Y").strftime("%Y-%m-%d")

            _, created = EpuIndexScore.objects.get_or_create(date=d,
                                                             number_of_articles=row[1],
                                                             number_of_papers=row[2],
                                                             epu=row[3])
            self.stdout.write('.', ending="")
            self.stdout.flush()
