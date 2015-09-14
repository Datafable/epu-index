from django.contrib import admin

from .models import EpuIndexScore, Article, NewsJournal, JournalsScraped


class ArticleAdmin(admin.ModelAdmin):
    list_filter = ('news_journal',)
    date_hierarchy = 'published_at'
    list_display = ('title', 'published_at', 'news_journal', 'epu_score')

class JournalsScrapedAdmin(admin.ModelAdmin):
    list_filter = ('journal',)
    date_hierarchy = 'date'
    list_display = ('date', 'journal')

admin.site.register(EpuIndexScore)
admin.site.register(Article, ArticleAdmin)
admin.site.register(NewsJournal)
admin.site.register(JournalsScraped, JournalsScrapedAdmin)
