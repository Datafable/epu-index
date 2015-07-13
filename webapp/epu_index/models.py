from django.db import models


class EpuIndexScore(models.Model):
    date = models.DateField()
    number_of_articles = models.IntegerField()
    number_of_papers = models.IntegerField()
    epu = models.FloatField()


class NewsJournal(models.Model):
    name = models.CharField(max_length=255)
    spider_name = models.CharField(max_lenght=255)


class Article(models.Model):
    news_journal = models.ForeignKey(NewsJournal)
    intro = models.TextField()
    url = models.URLField()
    title = models.CharField(max_length=255)
    text = models.TextField()
    published_at = models.DateTimeField()

    def __unicode__(self):
        return self.title
