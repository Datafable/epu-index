from django.db import models

# See stopwords_to_tuple.py to convert stopwords.txt to this constant.
STOPWORDS = ('aan', 'aangezien', 'achter', 'af', 'al', 'al', 'alle', 'allebei', 'alleen', 'allen', 'als', 'altijd','ander', 'andere', 'anderen', 'anders', 'anders', 'beetje', 'behalve', 'ben', 'bepaald', 'bij', 'boven', 'boven', 'bovenal', 'bovendien', 'bovengenoemd', 'bovenstaand', 'bovenvermeld', 'buiten', 'daar', 'daardoor', 'daarin', 'daarna', 'daarnet', 'daarom', 'dag', 'dan', 'dat', 'de', 'deel', 'deels', 'den', 'der', 'desondanks', 'deze', 'dicht', 'dichtbij', 'die', 'dit', 'door', 'doordat', 'dus', 'echter', 'een', 'eenmalig', 'eens', 'eerder', 'eerst', 'eerste', 'elk', 'elke', 'en', 'enige', 'enkele', 'enz', 'er', 'erboven', 'erdoor', 'ergens', 'erin', 'ernaast', 'eronder', 'etc', 'even', 'eveneens', 'evenwel', 'gauw', 'gedurende', 'gegeven', 'gekund', 'geleden', 'geweest', 'gisteren', 'haar', 'haarzelf', 'had', 'hadden', 'heb', 'hebben', 'heeft', 'heel', 'hem', 'hemzelf', 'hen', 'het', 'hier', 'hierdoor', 'hierin', 'hij', 'hoe', 'hoewel', 'hoogstwaarschijnlijk', 'hun', 'ieder', 'iedere', 'iedereen', 'iemand', 'iets', 'ik', 'in', 'inzake', 'is', 'je', 'jezelf', 'jij', 'jou', 'jouw', 'jullie', 'kan', 'kon', 'konden', 'kunnen', 'kunt', 'laatst', 'laatste', 'liever', 'maar', 'mag', 'me', 'mee', 'meer', 'met', 'mezelf', 'mij', 'mijn', 'minder', 'misschien', 'moest', 'moesten', 'moet', 'moeten', 'mogelijk', 'mogelijks', 'mogen', 'morgen', 'na', 'naar', 'naast', 'nabij', 'nadat', 'namelijk', 'neer', 'nergens', 'niemand', 'niet', 'niets', 'niettemin', 'nieuw', 'noch', 'nodig', 'nog', 'nogal', 'nu', 'of', 'om', 'omdat', 'omstreeks', 'omtrent', 'omver', 'ondanks', 'onder', 'ondertussen', 'ongeveer', 'onmiddellijk', 'ons', 'onszelf', 'onwaarschijnlijk', 'onze', 'ook', 'op', 'opnieuw', 'opzij', 'over', 'over', 'overigens', 'pas', 'precies', 'reeds', 'rond', 'rondom', 'sedert', 'sinds', 'sindsdien', 'slechts', 'sommige', 'sommigen', 'soms', 'steeds', 'tamelijk', 'te', 'tegen', 'ten', 'tenzij', 'ter', 'terwijl', 'thans', 'tijdens', 'toch', 'toen', 'toenmalig', 'tot', 'totdat', 'tussen', 'uit', 'uitgezonderd', 'vaak', 'van', 'van', 'vanaf', 'vandaag', 'vandaan', 'veel', 'ver', 'veraf', 'vervolgens', 'voldoende', 'volgende', 'volgens', 'voor', 'voor', 'vooral', 'voorbij', 'voordat', 'voordien', 'voorheen', 'voornamelijk', 'voorop', 'vooruit', 'vrij', 'vroeger', 'vroegere', 'waar', 'waardat', 'waarna', 'waarom', 'waarschijnlijk', 'wanneer', 'want', 'waren', 'was', 'wat', 'we', 'weinig', 'wel', 'welk', 'welke', 'wie', 'wiens', 'wij', 'wil', 'wilde', 'wilden', 'willen', 'wilt', 'word', 'worden', 'wordt', 'wou', 'ze', 'zeer', 'zeker', 'zekere', 'zich', 'zichzelf', 'zij', 'zijn', 'zo', 'zoal', 'zoals', 'zodat', 'zonder', 'zou', 'zouden', 'houden', 'houd', 'houdt', 'hield', 'hielden', 'geef', 'geven', 'geeft', 'gegeven', 'gaf', 'gaven', 'momenteel', 'procent', 'brengen', 'brengt', 'breng', 'bracht', 'brachten', 'gebracht', 'een', 'twee', 'drie', 'vier', 'vijf', 'zes', 'zeven', 'acht', 'negen', 'tien', 'elf', 'twaalf', 'dertien', 'veertien', 'vijftien', 'zestien', 'zeventien', 'achtien', 'negentien', 'twintig', 'maandag', 'dinsdag', 'woensdag', 'donderdag', 'vrijdag', 'zaterdag', 'zondag', 'week', 'maand', 'jaar', 'vorig', 'vorige', 'dag', 'weken', 'maanden', 'jaren', 'voorbije', 'dagen', 'rond', 'geen', 'wel', 'nieuw', 'oud', 'nieuwe', 'oude', 'aldus', 'lijkt', 'lijken', 'lijk', 'leken', 'hele', 'nog', 'zal', 'zullen', 'gaan', 'gaat', 'ga', 'ging', 'gingen', 'uit', 'januari', 'februari', 'maart', 'april', 'mei', 'juni', 'juli', 'augustus', 'september', 'oktober', 'november', 'december', 'jan', 'feb', 'apr', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec', 'sprake', 'blijven', 'blijf', 'blijft', 'bleef', 'bleven', 'aantal', 'miljard', 'miljoen', 'duizend', 'honderd', 'euro', 'dollar', 'yen', 'pond', 'zet', 'zetten', 'zette', 'gezet', 'mits', 'telt', 'tellen', 'klonk', 'klinken', 'klinkt', 'toont', 'tonen', 'toonde', 'oppert', 'opperde', 'opperen', 'meent', 'menen', 'meende', 'waardoor', 'komt', 'komen', 'kwam', 'werd', 'werden', 'weer', 'tweede', 'derde', 'vierde', 'vijfde', 'zesde', 'zevende', 'achtste', 'negende', 'tiende', 'elfde', 'twaalfde', 'dertiende', 'veertiende', 'vijftiende', 'zestiende', 'zeventiende', 'achttiende', 'negentiende', 'twintigste', 'honderdste', 'duizendste', 'dertig', 'veertig', 'vijftig', 'zestig', 'zeventig', 'tachtig', 'negentig', 'dertigste', 'veertigste', 'vijftigste', 'zestigste', 'zeventigste', 'tachtigste', 'negentigste')

ARTICLES_APU_CUTOFF = -0.15


class EpuIndexScore(models.Model):
    date = models.DateField(unique=True)
    number_of_articles = models.IntegerField()
    number_of_papers = models.IntegerField()
    epu = models.FloatField()

    def __unicode__(self):
        return '{0}: {1}'.format(self.date, self.epu)

    # We alias a field for the API
    def number_of_newspapers(self):
        return self.number_of_papers


class NewsJournal(models.Model):
    name = models.CharField(max_length=255)
    spider_name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


# This table/model stores a log of which scrapers successfully ran on a give day.
# It provides necessary data to calculate the EPU index of a given day. See issue #61 and #64
class JournalsScraped(models.Model):
    journal = models.ForeignKey(NewsJournal)
    date = models.DateField()

    class Meta:
        unique_together = ('journal', 'date')


class Article(models.Model):
    news_journal = models.ForeignKey(NewsJournal, null=True)
    intro = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    title = models.CharField(max_length=255)
    text = models.TextField()
    cleaned_text = models.TextField()
    published_at = models.DateTimeField()
    epu_score = models.DecimalField(max_digits=9, decimal_places=5, blank=True, null=True)

    def cleaned_text_without_stopwords(self):
        word_list = self.cleaned_text.lower().split()

        return ' '.join([i for i in word_list if i not in STOPWORDS])

    class Meta:
        unique_together = ("news_journal", "published_at", "title")

    def __unicode__(self):
        return self.title
