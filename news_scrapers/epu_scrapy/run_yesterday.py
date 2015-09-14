import os

# run spiders
for spider in ['demorgen',
    'deredactie',
    'standaard',
    'detijd',
    'gva',
    'hbvl',
    'hln',
    'nieuwsblad']:
    os.system('scrapy crawl {0}'.format(spider))
