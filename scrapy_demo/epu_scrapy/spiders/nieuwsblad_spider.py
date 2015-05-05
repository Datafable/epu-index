import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from epu_scrapy.items import Article

class WjnhSpider(CrawlSpider):
    name = 'nieuwsblad' # name of the spider, to be used when running from command line
    allowed_domains = ['www.nieuwsblad.be']
    start_urls = ['http://www.nieuwsblad.be/zoeken?keyword=economisch&daterange=today&datestart=&dateend=&categoryrange=00000000-0000-0000-0000-000000000000']
    rules = (
        Rule(LinkExtractor(allow=('zoeken\/.*page=[0-9]+'))),
        Rule(LinkExtractor(allow=('\/cnt\/')), callback='parse_article'),
    ) # if a link matches the pattern in 'allow', it will be followed. If 'callback' is given, that function will be executed with the page that the link points to.

    def parse_article(self, response):
        title = response.xpath('//article/div[2]/div/div/header/h1/text()').extract()[0].encode('utf-8')
        datetime_str = response.xpath('//article/div[2]/div/div/footer/p/time/@datetime').extract()[0].encode('utf-8')
        article_div = response.xpath('//article/div[2]/div/div/div[1]/div[2]')
        article_intro = article_div.xpath("div[@class='article__intro']/p/text()").extract()[0].encode('utf-8')
        article_full_text_fragments = article_div.xpath('p/text()|p/*/text()').extract()
        article_full_text = '\n'.join([x.encode('utf-8') for x in article_full_text_fragments])
        # now create an Article item, and return it. All Articles created during scraping will can be written to an output file when the -o option is given.
        article = Article()
        article['title'] = title
        article['datetime'] = datetime_str
        article['text'] = article_full_text
        return article
