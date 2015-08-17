from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils import timezone

from .models import Article


class TermFrequencyEndpointTests(TestCase):
    def setUp(self):
        article1 = Article.objects.create(published_at=timezone.now(),
                                          cleaned_text="is an article about de evolution evolution project",
                                          epu_score=0.4)

        article2 = Article.objects.create(published_at=timezone.now() - timezone.timedelta(days=1),
                                          cleaned_text="New Sinds book published about evolution nematodes week",
                                          epu_score=5)

        # We also create a negative EPU article that should always nver appear (per spec!)
        Article.objects.create(published_at=timezone.now(),
                               cleaned_text="evolution nematodes week",
                               epu_score=-1)

    def test_dates(self):
        # Test articles are correctly filtered according to start_date/ end_date

        # 1. no date filter, get everything
        #response = self.client.get(reverse('epu-term-frequency'))

        # 2. start date but no end

        # 3. end date but no start

        # 4. start and end filters are supplied

        #import pdb; pdb.set_trace()
        pass

    def test_lowercase(self):
        # Ensure words are returned as lowercase
        pass

    def test_stopwords(self):
        # Ensure Sinds was removed since it's in the stopwords list
        pass

    def test_count_words(self):
        # Ensure the evolution term appear 3 times (2 times in article1 and once in article2)
        pass

    def test_maxwords_parameter(self):
        pass

    def test_only_epu_positive_articles(self):
        response = self.client.get(reverse('epu-term-frequency'))

        # Let's check if we have only 3 evolution, 1 nematodes and 1 week
        # (otherwise, the EPU negative article has been taken into account)
        import pdb; pdb.set_trace()
        pass

