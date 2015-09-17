# -*- coding: utf-8 -*-
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from epu_index.models import NewsJournal, JournalsScraped
from django.db import IntegrityError
import datetime
from dateutil import parser
import json
import os
import re
import pandas as pd

class EpuScrapyPipeline(object):
    def open_spider(self, spider):
        import django
        django.setup()
        settingsfile = os.path.join(os.path.dirname(__file__), 'crawling_settings.json')
        self.settings = json.load(open(settingsfile))
        self.journals = {j.spider_name: j for j in NewsJournal.objects.all()}
        self.word_weights = self._read_model_file(os.path.join(os.path.dirname(settingsfile), self.settings['model_file']))
        self.REPLACE_CHARS = (
            (u'ë', u'e'),
            (u'ö', u'o'),
            (u'ü', u'u'),
            (u'ï', u'i'),
            (u'é', u'e'),
            (u'è', u'e'),
            (u'à', u'a'),
            (u'á', u'a'),
            (u'í', u'i'),
            (u'ì', u'i'),
            (u'ó', u'o'),
            (u'ò', u'o'),
            (u'ú', u'u'),
            (u'ù', u'u'),
            (u'ñ', u'n')
        )


    def close_spider(self, spider):
        if type(self.settings['period']) is dict:
            date_from = parser.parse(self.settings['period']['start'])
            date_end = parser.parse(self.settings['period']['end'])
            days_diff = date_end - date_from
            for d in range(days_diff.days + 1):
                scraped_date = date_from + datetime.timedelta(days=d)
                self._log_successful_crawl(scraped_date, spider)
        else:
            scraped_date = datetime.date.today() - datetime.timedelta(days=1)
            self._log_successful_crawl(scraped_date, spider)

    def process_item(self, item, spider):
        item['news_journal'] = self.journals[spider.name]
        if item['text'] != '':
            item['cleaned_text'] = self._clean_text(item['text'])
            item['epu_score'] = self._score_text(item['cleaned_text'])
        try:
            item.save()
        except IntegrityError, e:
            # article should be unique. This prevents us from inserting duplicate articles
            print '===> could not insert: <==='
            print e.message
        return item

    def _clean_text(self, intext):
        for char_tuple in self.REPLACE_CHARS:
            intext = intext.replace(char_tuple[0], char_tuple[1])
        return ' '.join(re.findall('\w+', intext, flags=re.UNICODE)).encode('utf-8')


    def _log_successful_crawl(self, scraped_date, spider):
        js = JournalsScraped(journal=self.journals[spider.name], date=scraped_date)
        try:
            js.save()
        except IntegrityError:
            pass


    def _read_model_file(self, filename):
        return pd.read_csv(filename, header=0, index_col=0)

    def _score_text(self, text):
        score = 0
        for word in text.split(' '):
            if word.lower() in self.word_weights.index:
                score += self.word_weights.loc[word.lower()]['weight']
        return score

