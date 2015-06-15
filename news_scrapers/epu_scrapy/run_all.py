from datetime import datetime
from subprocess import call

today = datetime.today()
spiders = [
    'demorgen',
    'nieuwsblad',
    'hbvl',
    'hln',
    'gva',
    'deredactie',
]

for spider in spiders:
    command = 'scrapy crawl {0} -o {0}_{1}.json'.format(spider, today.strftime('%Y-%m-%d'))
    call(['scrapy', 'crawl', spider, '-o', '{0}_{1}.json'.format(spider, today.strftime('%Y-%m-%d'))])
