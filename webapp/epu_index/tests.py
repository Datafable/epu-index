import json

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.core.management import call_command

from .models import Article


class TermFrequencyEndpointTests(TestCase):
    def setUp(self):
        Article.objects.create(published_at=timezone.now() - timezone.timedelta(days=1),
                               cleaned_text="New Sinds book published about Evolution nematodes weeke",
                               epu_score=-0.13)

        Article.objects.create(published_at=timezone.now(),
                               cleaned_text="is an article about de evolution EVOLUTION project",
                               epu_score=0.4)

        Article.objects.create(published_at=timezone.now() + timezone.timedelta(days=1),
                               cleaned_text="Some other words",
                               epu_score=2)

        # We also create an EPU article that should never appear (per spec!) because its EPU score
        # is under cutoff treshold
        Article.objects.create(published_at=timezone.now(),
                               cleaned_text="evolution nematodes weeke",
                               epu_score=-0.16)

        call_command('calculate_all_words_per_day')

    def test_dates(self):
        # Test articles are correctly filtered according to start_date/ end_date

        # 1. no date filter, get everything
        response = self.client.get(reverse('epu-term-frequency'))
        r_python = json.loads(response.content)

        # Will throw StopIteration if article of yesteray is not taken into account
        next(x for x in r_python if x['word'] == 'book')
        next(x for x in r_python if x['word'] == 'article')  # Idem for today's article
        next(x for x in r_python if x['word'] == 'words')  # And for tomorrow's

        # 2. start date but no end (we should not find yesterday's article)
        today_str = timezone.now().date().isoformat()
        response = self.client.get(reverse('epu-term-frequency'), {'start_date': today_str})
        r_python = json.loads(response.content)

        with self.assertRaises(StopIteration):
            next(x for x in r_python if x['word'] == 'book')
        next(x for x in r_python if x['word'] == 'article')
        next(x for x in r_python if x['word'] == 'words')

        # 3. end date but no start
        response = self.client.get(reverse('epu-term-frequency'), {'end_date': today_str})
        r_python = json.loads(response.content)

        next(x for x in r_python if x['word'] == 'book')
        next(x for x in r_python if x['word'] == 'article')  # Idem for today's article
        with self.assertRaises(StopIteration):
            next(x for x in r_python if x['word'] == 'words')

        # 4. start and end filters are supplied
        response = self.client.get(reverse('epu-term-frequency'), {'start_date': today_str,
                                                                   'end_date': today_str})
        r_python = json.loads(response.content)

        with self.assertRaises(StopIteration):
            next(x for x in r_python if x['word'] == 'book')
        next(x for x in r_python if x['word'] == 'article')
        with self.assertRaises(StopIteration):
            next(x for x in r_python if x['word'] == 'words')

    def test_lowercase(self):
        # Ensure words are returned as lowercase
        # Evolution appear 3 times with 3 different spellings, results should be merged.
        response = self.client.get(reverse('epu-term-frequency'))

        evolution_r = next(x for x in json.loads(response.content) if x['word'] == 'evolution')
        self.assertEqual(evolution_r['count'], 3)

        # The non-lowercase forms don't appear:
        with self.assertRaises(StopIteration):
            next(x for x in json.loads(response.content) if x['word'] == 'EVOLUTION')
        with self.assertRaises(StopIteration):
            next(x for x in json.loads(response.content) if x['word'] == 'Evolution')

    def test_stopwords(self):
        # Ensure Sinds was removed since it's in the stopwords list
        response = self.client.get(reverse('epu-term-frequency'))

        with self.assertRaises(StopIteration):
            next(x for x in json.loads(response.content) if x['word'] == 'Sinds')

    def test_maxwords_parameter(self):
        # There's no reason to have only 3 words, unless the max_words parameter works
        response = self.client.get(reverse('epu-term-frequency'), {'max_words': 3})
        self.assertEqual(len(json.loads(response.content)), 3)

    def test_bigger_numbers_first(self):
        response = self.client.get(reverse('epu-term-frequency'))
        response_python = json.loads(response.content)

        self.assertGreaterEqual(response_python[0]['count'], response_python[1]['count'])
        self.assertGreaterEqual(response_python[1]['count'], response_python[2]['count'])
        self.assertGreaterEqual(response_python[2]['count'], response_python[3]['count'])
        self.assertGreaterEqual(response_python[3]['count'], response_python[4]['count'])
        self.assertGreaterEqual(response_python[4]['count'], response_python[5]['count'])

    def test_only_epu_positive_articles(self):
        response = self.client.get(reverse('epu-term-frequency'))

        # Let's check if we have only 3 evolution, 1 nematodes and 1 week1
        # (otherwise, the EPU negative article has been taken into account)
        evolution_r = next(x for x in json.loads(response.content) if x['word'] == 'evolution')
        self.assertEqual(evolution_r['count'], 3)

        nematodes_r = next(x for x in json.loads(response.content) if x['word'] == 'nematodes')
        self.assertEqual(nematodes_r['count'], 1)

        week_r = next(x for x in json.loads(response.content) if x['word'] == 'weeke')
        self.assertEqual(week_r['count'], 1)
