from django.contrib import admin

from .models import EpuIndexScore, Article, NewsJournal

admin.site.register(EpuIndexScore)
admin.site.register(Article)
admin.site.register(NewsJournal)
