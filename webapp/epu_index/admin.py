from django.contrib import admin

from .models import EpuIndexScore, Article, NewsJournal

class ArticleAdmin(admin.ModelAdmin):
    list_filter = ('news_journal',)
    date_hierarchy= 'published_at'
    list_display = ('title', 'published_at', 'news_journal', 'epu_score')


admin.site.register(EpuIndexScore)
admin.site.register(Article, ArticleAdmin)
admin.site.register(NewsJournal)
