from django.db import models

# See stopwords_to_tuple.py to convert stopwords.txt to this constant.
STOPWORDS = ('dus', 'zo', 'zoal', 'zoals', 'ove', 'boven', 'bovendien', 'bovenal', 'volgens',
             'na', 'nadat', 'tegen', 'al', 'ook', 'altijd', 'iemand', 'waar', 'waardat',
             'waarna', 'elk', 'elke', 'rond', 'omdat', 'want', 'voordat', 'voordien', 'voor',
             'achter', 'tussen', 'voorbij', 'door', 'met', 'doordat', 'zeker', 'zekere', 'neer',
             'ergens', 'anders', 'ander', 'andere', 'voldoende', 'iedereen', 'ieder', 'iedere',
             'behalve', 'weinig', 'vroeger', 'vroegere', 'vervolgens', 'volgens', 'gegeven',
             'dat', 'zich', 'zichzelf', 'jezelf', 'hoewel', 'mezelf', 'ondanks', 'desondanks',
             'onmiddellijk', 'laatst', 'laatste', 'voornamelijk', 'niettemin', 'sinds', 'soms',
             'hen', 'hun', 'hem', 'haar', 'jou', 'jouw')


class EpuIndexScore(models.Model):
    date = models.DateField(unique=True)
    number_of_articles = models.IntegerField()
    number_of_papers = models.IntegerField()
    epu = models.FloatField()

    def __unicode__(self):
        return '{0}: {1}'.format(self.date, self.epu)

    # We alias a field for the API
    def number_of_newspapers(self):
        return self.number_of_papers


class NewsJournal(models.Model):
    name = models.CharField(max_length=255)
    spider_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


# This table/model stores a log of which scrapers successfully ran on a give day.
# It provides necessary data to calculate the EPU index of a given day. See issue #61 and #64
class JournalsScraped(models.Model):
    journal = models.ForeignKey(NewsJournal)
    date = models.DateField()

    class Meta:
        unique_together = ('journal', 'date')


class Article(models.Model):
    news_journal = models.ForeignKey(NewsJournal, null=True)
    intro = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    cleaned_text = models.TextField()
    published_at = models.DateTimeField()
    epu_score = models.DecimalField(max_digits=9, decimal_places=5, blank=True, null=True)

    def cleaned_text_without_stopwords(self):
        word_list = self.cleaned_text.lower().split()

        return ' '.join([i for i in word_list if i not in STOPWORDS])

    class Meta:
        unique_together = ("news_journal", "published_at", "title")

    def __unicode__(self):
        return self.title
