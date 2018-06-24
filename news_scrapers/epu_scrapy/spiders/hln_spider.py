import json
import os
from scrapy.contrib.spiders import CrawlSpider
from scrapy import Request
from epu_scrapy.items import Article


def set_start_urls(settings):
    """
    Based on the dates given in the settings file, construct the start urls for the spider
    """
    term = settings['term']
    start_urls = ['http://www.hln.be/zoeken?query={}'.format(term)]
    return start_urls


class HetLaatsteNieuwsSpider(CrawlSpider):
    name = 'hln' # name of the spider, to be used when running from command line
    allowed_domains = ['www.hln.be']
    settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = set_start_urls(settings)
    pagesize = 20

    def parse(self, response):
        """
        Parse the first search page get article detail links
        """
        articles = response.css('ul.search-results__list article')
        for article in articles:
            yield Request(article.xpath('.//a/@href').extract_first(), self.parse_article)

    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('//article/header/h1/text()').extract()
        if len(title_parts) > 0:
            title = title_parts[0]
        else:
            title = ''

        # search for article published date
        datetime_str_parts = response.xpath('//article/header/ul/descendant::time/@datetime').extract()
        if len(datetime_str_parts) > 0:
            datetime_str = ' '.join(x for x in datetime_str_parts)
        else:
            datetime_str = ''

        # search for article intro text
        article_intro_parts = response.xpath('//article/header').css('div.article__text--intro').xpath('./descendant-or-self::*/text()').extract()
        article_intro = ' '.join([x.strip() for x in article_intro_parts])

        # search for article full text
        article_text_sections = response.xpath('//article').css('p.article__text').xpath('./descendant-or-self::*/text()').extract()

        article_full_text = '\n'.join([x.strip() for x in article_text_sections]).strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['published_at'] = datetime_str
        article['text'] = article_full_text
        return article
