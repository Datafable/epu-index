# -*- coding: utf-8 -*-

import csv
import urllib2
import time
import datetime

from django.core.management.base import BaseCommand

from epu_index.models import Article, NewsJournal

DELIMITER = '\t'
QUOTECHAR = "'"


def translate_journal(name):
    # Key: identifier in CSV file
    # Value: spîder_name in database
    journals = {
        'DeStandaard': 'standaard',
        'DeTijd': 'detijd',
        'DeRedactie': 'deredactie',
        'DeMorgen': 'demorgen',
        'Nieuwsblad': 'nieuwsblad',
        'HLN': 'hln'
    }
    return journals[name]


class Command(BaseCommand):
    help = 'Load CSV file to populate Article model. Journals should be loaded before so foreign\
    keys are set appropriately'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('csv_url')

        parser.add_argument('--truncate',
                            action='store_true',
                            dest='truncate',
                            default=False,
                            help='Truncate Article table before import.')

    def handle(self, *args, **options):
        csvfile = urllib2.urlopen(options['csv_url'])
        reader = csv.reader(csvfile, delimiter=DELIMITER, quotechar=QUOTECHAR)

        if options['truncate']:
            self.stdout.write('Truncating Article data table...')
            Article.objects.all().delete()

        for row in reader:
            published_at, journal, title, cleaned_text, epu = row

            dt = datetime.datetime(*time.strptime(published_at, '%a %b %d %H %M %S %Y')[0:6])
            dt_str = dt.isoformat() + '+00'  # assume all datetimes are in UTC
            spider_name = translate_journal(journal)

            journal = NewsJournal.objects.get(spider_name=spider_name)

            Article.objects.create(published_at=dt_str,
                                   news_journal=journal,
                                   text=cleaned_text,
                                   cleaned_text=cleaned_text,
                                   title=title,
                                   epu_score=float(epu))

            self.stdout.write('.', ending="")
            self.stdout.flush()
