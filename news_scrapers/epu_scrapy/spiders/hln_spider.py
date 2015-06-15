import json
import os
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.exceptions import CloseSpider
from scrapy import Request
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
        if settings['period'] is not 'yesterday':
            CloseSpider("unknown period setting. See the scrapers README for more information.")
        yesterday = today - timedelta(days=1)
        start_str = yesterday.strftime('%d%m%Y')
        end_str = today.strftime('%d%m%Y')
    else:
        start = datetime(*strptime(settings['period']['start'], '%Y-%m-%d')[:6]) # awkward syntax to convert struct time to datetime (see: http://stackoverflow.com/questions/1697815/how-do-you-convert-a-python-time-struct-time-object-into-a-datetime-object)
        start_str = start.strftime('%d%m%Y')
        end = datetime(*strptime(settings['period']['end'], '%Y-%m-%d')[:6])
        end_str = end.strftime('%d%m%Y')
    start_urls = ['http://www.hln.be/hln/article/searchResult.do?language=nl&searchValue={0}&startSearchDate={1}&endSearchDate={2}'.format(term, start_str, end_str)]
    return start_urls


class HetLaatsteNieuwsSpider(CrawlSpider):
    name = 'hln' # name of the spider, to be used when running from command line
    allowed_domains = ['www.hln.be']
    settings = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'crawling_settings.json')))
    start_urls = set_start_urls(settings)
    # if a link matches the pattern in 'allow', it will be followed. If 'callback' is given, that function will be
    # executed with the page that the link points to.
    rules = (
        Rule(SgmlLinkExtractor(allow=('search.dhtml\?.*page=[0-9]+'), restrict_xpaths=('//*[@id="searchResultBox"]'))),
        Rule(SgmlLinkExtractor(allow=('\/article\/detail\/'), restrict_xpaths=('//*[@id="searchResultBox"]')),
             callback='parse_article'),
    )
    pagesize = 20


    def parse(self, response):
        """
        Parse the first search page to determine the number of articles returned. Use the urls page parameter
        to iterate over all response pages and yield scrapy.Request objects that will be parsed with the
        parse_list_page function
        """
        nr_of_articles_element = response.xpath('//body/h4/b/text()').extract()
        if len(nr_of_articles_element) is 1:
            nr_of_articles = int(re.findall('[0-9]+', nr_of_articles_element[0].encode('utf-8'))[0])
            for i in range(0, 1 + nr_of_articles / self.pagesize):
                yield Request(self.start_urls[0] + '&resultAmountPerPage={0}&page={1}'.format(self.pagesize, i),
                              callback=self.parse_list_page)
        else:
            raise CloseSpider("could not parse number of articles from {0}".format(response.url))


    def parse_list_page(self, response):
        """
        Parse a single page returned by the search query. Find all links referring to articles and yield
        Request objects for every link found. The parsing of these links is done by the parse_article
        function.
        """
        print response.url
        links = response.xpath('//a/@href').extract()
        link_set = set([x.encode('utf-8') for x in links])
        for l in link_set:
            if re.search('article/detail', l):
                yield Request('http://www.hln.be' + l, callback=self.parse_article)


    def parse_article(self, response):
        # search for article title
        title_parts = response.xpath('//*[@id="articleDetailTitle"]/text()').extract()
        if len(title_parts) > 0:
            title = title_parts[0].encode('utf-8')
        else:
            title = ''

        # search for article published date
        datetime_str_parts = response.xpath('//article/div/section[@id="detail_content"]/span/text()').extract()
        if len(datetime_str_parts) > 0:
            datetime_full_str = ' '.join(x.encode('utf-8') for x in datetime_str_parts)
            datetime_str_in = re.findall('[0-9]+/[0-9]+/[0-9]+', datetime_full_str)[0]
            dt = datetime(*strptime(datetime_str_in, '%d/%m/%y')[:6])
            datetime_str = dt.strftime('%Y-%m-%d')
        else:
            datetime_str = ''

        # search for article intro text
        article_intro_paragraph = response.xpath('//article/descendant::*/p[contains(concat(" ", normalize-space(@class), " "), " intro ")]')
        article_intro_parts = article_intro_paragraph.xpath('descendant-or-self::*/text()').extract()
        article_intro = ' '.join([x.strip().encode('utf-8') for x in article_intro_parts])

        # search for article full text
        article_text_sections = response.xpath('//article/descendant-or-self::*/section[contains(concat(" ", normalize-space(@class), " "), " clear ")]')
        text_fragments = []

        # Parse text sections one by one
        for section in article_text_sections:
            # Remove unneeded content
            # Inner set:difference will remove a <ul class="read_more"> element, that contains links to related pages
            # Outer set:difference will remove child <section> elements from other <section> elements. They contain side
            # images and other stuff.
            raw_text_fragments = section.xpath('''
            set:difference(
                set:difference(
                    ./descendant-or-self::*/text(),
                    .//ul[contains(concat(" ", normalize-space(@class), " "), " read_more ")]/descendant-or-self::*/text()
                ),
                .//section/descendant-or-self::*/text()
            )
            ''').extract()
            text_fragments += raw_text_fragments

        article_full_text = '\n'.join([x.strip().encode('utf-8') for x in text_fragments]).strip()

        # now create an Article item, and return it. All Articles created during scraping can be written to an output file when the -o option is given.
        article = Article()
        article['url'] = response.url
        article['intro'] = article_intro
        article['title'] = title
        article['datetime'] = datetime_str
        article['text'] = article_full_text
        return article
