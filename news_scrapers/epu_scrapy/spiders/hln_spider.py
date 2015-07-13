import json
import os
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.exceptions import CloseSpider
from scrapy import Request
from epu_scrapy.items import Article
from datetime import datetime, timedelta, date
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
            if 'leverde geen resultaten op' in response.body:
                raise CloseSpider('No search results for this query.')
            raise CloseSpider('Could not parse number of articles from {0}'.format(response.url))

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
            print datetime_full_str
            # Explaining the regular expression at line 100:
            #     (?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)[^\d]*(?P<hour>\d+)u(?P<minutes>\d+) contains several parts:
            #
            #     (?<day>\d+)/(?P<month>\d+)/(?P<year>\d+)  => 3 numbers separated by front slashes '/'. Each number is
            #             surrounded by round brackets and the (?P<name>...) construct. This means that for each matching
            #             pattern in the brackets (in each case this is simply '\d+' meaning: a number, possibly
            #             containing multiple digits) a group will be created with the name given in the square brackets.
            #             In this case, three groups are made, one called "day", one "month" and one "year". The matched
            #             string for every group can easily be retrieved later from the returned match object. This is
            #             done at line 104.
            #     [^\d]*         => Any number of non-digit characters. This string separates the day from the time.
            #     (?P<hour>\d+)u(?P<minutes>\d+)    => Two numbers separated by the character 'u' (hour and minutes).
            #             Again, every matching number is assigned to a group, one for "hour" and one for "minutes".
            m = re.search(
                '(?P<day>\d+)/(?P<month>\d+)/(?P<year>\d+)[^\d]*(?P<hour>\d+)u(?P<minutes>\d+)',
                datetime_full_str
            )
            if m:
                datetime_parts = ['20' + m.group('year'), m.group('month'), m.group('day'), m.group('hour'), m.group('minutes')]
                dt = datetime(*[int(x) for x in datetime_parts])
                datetime_str = dt.isoformat()
            else:
                datetime_str = 'could not parse'
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
        article['journal'] = self.name
        return article
