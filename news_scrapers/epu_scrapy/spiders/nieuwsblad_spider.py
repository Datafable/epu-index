import json
import os
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.exceptions import CloseSpider
from epu_scrapy.items import Article
from datetime import datetime, timedelta
from time import strptime


def set_start_urls(settings):
    """
    Based on the dates given in the settings file, construct the start urls for the spider
    """
    term = settings['term']
    if type(settings['period']) is not dict:
        today = datetime.today()
        if settings['period'] != 'yesterday':
            CloseSpider("unknown period setting. See the scrapers README for more information.")
        search_day = today - timedelta(days=1) # search for articles of yesterday
        search_day_str = '{0}/{1}/{2}'.format(search_day.day, search_day.month, search_day.year)
        start_str = search_day_str
        end_str = search_day_str
    else:
        start = datetime(*strptime(settings['period']['start'], '%Y-%m-%d')[:6]) # awkward syntax to convert struct time to datetime (see: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object)
        start_str = '{0}/{1}/{2}'.format(start.day, start.month, start.year)
        end = datetime(*strptime(settings['period']['end'], '%Y-%m-%d')[:6])
        end_str = '{0}/{1}/{2}'.format(end.day, end.month, end.year)
    start_urls = ['http://www.nieuwsblad.be/zoeken/?keyword={0}&datestart={1}&dateend={2}'.format(term, start_str, end_str)]
    return start_urls


class NieuwsbladSpider(CrawlSpider):
    name = 'nieuwsblad' # name of the spider, to be used when running from command line
    allowed_domains = ['www.nieuwsblad.be']
    settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = set_start_urls(settings)
    rules = (
        Rule(LinkExtractor(allow=('zoeken[?/].*page=[0-9]+'))),
        Rule(LinkExtractor(allow=('\/cnt\/')), callback='parse_article'),
    ) # if a link matches the pattern in 'allow', it will be followed. If 'callback' is given, that function will be executed with the page that the link points to.

    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('//article/div[2]/div/div/header/h1/text()').extract()
        if len(title_parts) > 0:
            title = title_parts[0].encode('utf-8')
        else:
            title = ''

        # search for article published date
        datetime_str_parts = response.xpath('//article/div[2]/div/div/footer/p/time/@datetime').extract()
        if len(datetime_str_parts) > 0:
            dt = datetime(*strptime(datetime_str_parts[0].encode('utf-8').split('+')[0], '%Y-%m-%d %H:%M')[0:6])
            datetime_str = dt.isoformat()
        else:
            datetime_str = ''

        # search for div containing all article content
        article_div = response.xpath('//article/div[2]/div/div/div[1]/div[@class="article__body"]')

        # search for article intro text
        article_intro_parts = article_div.xpath('div[@class="article__intro"]/descendant-or-self::text()').extract()
        article_intro = ' '.join([x.strip() for x in article_intro_parts])

        # search for article full text
        article_full_text_fragments = article_div.xpath('div[@class="article__intro"]/following-sibling::*/text()').extract()
        article_full_text = '\n'.join([x.strip() for x in article_full_text_fragments]).strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['published_at'] = datetime_str
        article['text'] = article_full_text
        return article
