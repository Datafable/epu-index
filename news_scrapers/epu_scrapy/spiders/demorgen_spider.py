import json
import os
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
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
        if settings['period'] == 'yesterday':
            search_day = today - timedelta(days=1) # search for articles of yesterday
        elif settings['period'] == 'today':
            search_day = today
        search_day_str = '{0}-{1}-{2}'.format(search_day.day, search_day.month, search_day.year)
        start_urls = ['http://www.demorgen.be/zoek/?query={0}&sorting=DATE_DESC&date=RANGE&from={1}&to={2}'.format(term, search_day_str, search_day_str)]
    else:
        start = datetime(*strptime(settings['period']['start'], '%Y-%m-%d')[:6]) # awkward syntax to convert struct time to datetime (see: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object)
        start_str = '{0}-{1}-{2}'.format(start.day, start.month, start.year)
        end = datetime(*strptime(settings['period']['end'], '%Y-%m-%d')[:6])
        end_str = '{0}-{1}-{2}'.format(end.day, end.month, end.year)
        start_urls = ['http://www.demorgen.be/zoek/?query={0}&sorting=DATE_DESC&date=RANGE&from={1}&to={2}'.format(term, start_str, end_str)]
    return start_urls


class DemorgenSpider(CrawlSpider):
    name = 'demorgen' # name of the spider, to be used when running from command line
    allowed_domains = ['www.demorgen.be']
    settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = set_start_urls(settings)
    rules = (
        Rule(SgmlLinkExtractor(allow=('zoek\/.*LAST_WEEK.*page=[0-9]+'))),
        Rule(SgmlLinkExtractor(allow=('www.demorgen.be\/[^\/]+\/[^\/]+'), restrict_xpaths=('//ul[contains(concat(" ", normalize-space(@class), " "), " articles-list ")]')),
             callback='parse_article'),
    ) # if a link matches the pattern in 'allow', it will be followed. If 'callback' is given, that function will be executed with the page that the link points to.

    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('//article/div/header/h1/text()').extract()
        if len(title_parts) > 0:
            title = title_parts[0].encode('utf-8')
        else:
            title = ''

        # search for article published date
        datetime_str_parts = response.xpath('//article/div/footer/descendant::*/time/@datetime').extract()
        if len(datetime_str_parts) > 0:
            datetime_str = datetime_str_parts[0].encode('utf-8')
        else:
            datetime_str = ''

        # search for div containing all article content. See this SO post that explains why such a complicated XPath selector
        # is used: http://stackoverflow.com/questions/1390568/how-to-match-attributes-that-contain-a-certain-string
        article_div = response.xpath('//article/descendant::*/div[contains(concat(" ", normalize-space(@class), " "), " article__body ")]')

        # search for article intro text
        article_intro_parts = article_div.xpath('*[contains(concat(" ", normalize-space(@class), " "), " article__intro ")]/text()').extract()
        article_intro = ' '.join([x.strip().encode('utf-8') for x in article_intro_parts])

        # search for article full text
        article_full_text_fragments = article_div.xpath('div[@itemprop="articleBody"]/descendant::*/text()').extract()
        article_full_text = '\n'.join([x.strip().encode('utf-8') for x in article_full_text_fragments]).strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['datetime'] = datetime_str
        article['text'] = article_full_text
        return article
