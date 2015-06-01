import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from epu_scrapy.items import Article
from datetime import datetime, timedelta
from time import strptime, strftime
import re

class DeredactieSpider(CrawlSpider):
    name = 'deredactie' # name of the spider, to be used when running from command line
    allowed_domains = ['deredactie.be']
    today = datetime.today()
    search_day = today - timedelta(days=1) # search for articles of yesterday
    search_day_str = '{0}/{1}/{2}'.format(search_day.day, search_day.month, search_day.year % 100)
    pagesize = 20
    start_urls = ['http://deredactie.be/cm/vrtnieuws/1.516538?text=economie&type=text&range=atdate&isdate={0}&sort=date&action=submit&advancedsearch=on'.format(search_day_str)]

    def parse(self, response):
        """
        Parse the first search page to determine the number of articles returned. Use the urls offset parameter
        to iterate over all response pages and yield scrapy.Request objects that will be parsed with the
        parse_list_page function
        """
        nr_of_articles_element = response.xpath('//li[contains(concat(" ", normalize-space(@class), " "), " searchcounter ")]/text()').extract()
        if len(nr_of_articles_element) is 2:
            # nr of articles is mentioned above list of articles and below. So the number of elements that match the xpath selector is 2
            nr_of_articles = int(re.findall('[0-9]+', nr_of_articles_element[0].encode('utf-8'))[0])
            for i in range(0, nr_of_articles, self.pagesize):
                yield scrapy.Request(self.start_urls[0] + '&offset={0}'.format(i), callback=self.parse_list_page)
        else:
            raise scrapy.exceptions.CloseSpider("could not parse number of articles from {0}".format(response.url))


    def parse_published_datetime(self, datetime_element_parts):
        """
        Helper method to parse a datetime from a html element
        """
        datetime_str_parts = [x.encode('utf-8') for x in datetime_element_parts]
        datetime_str = ' '.join(datetime_str_parts).strip()
        datetime_str_stripped = re.findall('[0-9]+/[0-9]+/[0-9]+[^0-9]+[0-9]+:[0-9]+', datetime_str)[0]
        dt = strptime(datetime_str_stripped, '%d/%m/%Y - %H:%M')
        datetime_iso_str = strftime('%Y-%m-%d %H:%M', dt)
        return datetime_iso_str


    def parse_list_page(self, response):
        """
        Parse a single page returned by the search query. Find all links referring to articles and yield
        scrapy.Request objects for every link found. The parsing of these links is done by the parse_article
        function.
        """
        print response.url
        links = response.xpath('//div[contains(concat(" ", normalize-space(@class), " "), " searchresults ")]/descendant::a/@href').extract()
        link_set = set([x.encode('utf-8') for x in links])
        for l in link_set:
            if l is not '#':
                # an article link can point to a single article page, or a storyline page, which includes several articles.
                # in both cases, the id of the actual article that is pointed to can be found in the url. In the case
                # of a storyline, the url is like /cm/vrtnieuws/buitenland/<storylineid>?eid=<articleid> while for a
                # single article page, the url is /cm/vrtnieuws/binnenland/<articleid>. Both a storylineid and a articleid
                # look something like 1.193019, which will be matched by the regular expression pattern [0-9.]+
                article_id = re.findall('[0-9.]+', l)[-1] # the last id in the url is the article id
                l = 'http://deredactie.be/cm/' + article_id
                yield scrapy.Request(l, callback=self.parse_article)


    def parse_article(self, response):
        """
        Parse the article content page
        """

        # search for article title
        title_parts = response.xpath('//div[@id="articlehead"]/h1/text()').extract()
        if len(title_parts) > 0:
            title = ' '.join(set(title_parts)).encode('utf-8').strip()
        else:
            title = ''

        # search for article published date
        datetime_element_parts = response.xpath('//small[@id="pubdate"]/strong/text()').extract()
        if len(datetime_element_parts) > 0:
            datetime_iso_str = self.parse_published_datetime(datetime_element_parts)
        else:
            datetime_iso_str = ''

        # search for article intro text
        article_intro_parts = response.xpath('//div[@id="intro"]/strong/text()').extract()
        article_intro = ' '.join([x.strip().encode('utf-8') for x in article_intro_parts]).strip()

        # search for article full text
        article_full_text_fragments = response.xpath('//div[@id="articlebody"]/descendant::p/descendant-or-self::*/text()').extract()
        article_full_text = ' '.join([x.strip().encode('utf-8') for x in article_full_text_fragments]).strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['datetime'] = datetime_iso_str
        article['text'] = article_full_text
        return article