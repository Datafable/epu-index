import os
from datetime import date, timedelta

# calculate daily epu index and word counts
day = date(2013, 12, 10)

yesterday = date.today() - timedelta(days=1)

while day < yesterday:
    os.system('python manage.py calculate_daily_epu {0}'.format(day.isoformat()))
    os.system('python manage.py calculate_words_per_day {0}'.format(day.isoformat())
    day += timedelta(days=1)


# check spiders
os.system('python manage.py check_failed_scrapers')