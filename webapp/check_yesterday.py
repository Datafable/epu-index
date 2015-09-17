import os
from datetime import date, timedelta

# calculate daily epu index
yesterday = date.today() - timedelta(days=1)
os.system('python manage.py calculate_daily_epu {0}'.format(yesterday.isoformat()))


# check spiders
os.system('python manage.py check_failed_scrapers')
