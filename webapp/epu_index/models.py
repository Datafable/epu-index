from django.db import models


class EpuIndexScore(models.Model):
    date = models.DateField()
    number_of_articles = models.IntegerField()
    number_of_papers = models.IntegerField()
    epu = models.FloatField()
