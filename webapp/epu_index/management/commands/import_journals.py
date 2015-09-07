import csv
import urllib2

from django.core.management.base import BaseCommand

from epu_index.models import NewsJournal

DELIMITER = ';'


class Command(BaseCommand):
    help = 'Load CSV file to populate NewsJournal model.'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('csv_url')

        parser.add_argument('--truncate',
                            action='store_true',
                            dest='truncate',
                            default=False,
                            help='Truncate NewsJournal table before import.')

    def handle(self, *args, **options):
        csvfile = urllib2.urlopen(options['csv_url'])

        reader = csv.reader(csvfile, delimiter=DELIMITER)

        # We truncate only after successfully opening the CSV file...
        if options['truncate']:
            self.stdout.write('Truncating NewsJournal data table...')
            NewsJournal.objects.all().delete()

        for row in reader:
            NewsJournal.objects.create(name=row[0], spider_name=row[1])

            self.stdout.write('.', ending="")
            self.stdout.flush()
