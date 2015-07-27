from django.db import models


class EpuIndexScore(models.Model):
    date = models.DateField()
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


class Article(models.Model):
    news_journal = models.ForeignKey(NewsJournal, null=True)
    intro = models.TextField(blank=True, null=True)
    url = models.URLField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    cleaned_text = models.TextField()
    published_at = models.DateTimeField()
    epu_score = models.DecimalField(max_digits=9, decimal_places=5, blank=True, null=True)

    def __unicode__(self):
        return self.title
