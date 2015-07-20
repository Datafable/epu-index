# Quick and dirty script to migrate existing data into the django database
# This script should be replaced by Django migrate commands.

import csv
import psycopg2 as pg
import sys
import time
import datetime

def print_help():
    print """usage: migrate_data.py <journals csv> <articles csv> <epu index csv>

    journals csv:   csv file containing journal name and spider name of all scraped journals

    articles csv:   csv file containing journal, date time, url, title, intro, text of articles

    epu index csv:  csv file containing date, number of articles, number of journals and epu index
"""

def check_arguments():
    return sys.argv[1:]


def get_db_connection():
    return pg.connect(database='epu_index_dev01', user='bart_aelterman', host='localhost', port='5432')


def migrate_journals(incsv):
    journals = {}
    with open(incsv) as f:
        with get_db_connection() as conn:
            with conn.cursor() as curs:
                r = csv.reader(f, delimiter=';')
                i = 1
                for row in r:
                    curs.execute('insert into epu_index_newsjournal (id, name, spider_name) values (%s, %s, %s)', (i, row[0], row[1]))
                    journals[row[1]] = i
                    i += 1
    return journals

def translate_journal(name):
    journals = {
        'DeStandaard': 'standaard',
        'DeTijd': 'detijd',
        'DeRedactie': 'deredactie',
        'DeMorgen': 'demorgen',
        'Nieuwsblad': 'nieuwsblad',
        'HLN': 'hln'
    }
    return journals[name]


def migrate_articles(incsv, journals):
    with open(incsv) as f:
        with get_db_connection() as conn:
            with conn.cursor() as curs:
                r = csv.reader(f, delimiter=';')
                for row in r:
                    published_at, journal, title, text = row
                    url = 'not provided'
                    dt = datetime.datetime(*time.strptime(published_at, ' %b %d %H %M %S %Y')[0:6])
                    dt_str = dt.isoformat()
                    spider = translate_journal(journal)
                    journal_id = journals[spider]
                    curs.execute('insert into epu_index_article (url, published_at, news_journal_id, text, title) values (%s, %s, %s, %s, %s)',
                                 (url, dt_str, journal_id, text, title))

def migrate_epu_index(incsv):
    with open(incsv) as f:
        with get_db_connection() as conn:
            with conn.cursor() as curs:
                r = csv.reader(f, delimiter=';')
                header = r.next()
                for row in r:
                    date, nr_articles, nr_newspapers, epu = row
                    curs.execute('insert into epu_index_epuindexscore (date, number_of_articles, number_of_papers, epu) values (%s, %s, %s, %s)',
                                 (date, nr_articles, nr_newspapers, epu))

def main():
    if len(sys.argv) is not 4:
        print_help()
        sys.exit(-1)
    journals_csv, articles_csv, epu_index_csv = check_arguments()
    journals = migrate_journals(journals_csv)
    migrate_articles(articles_csv, journals)
    migrate_epu_index(epu_index_csv)


if __name__ == '__main__':
    main()