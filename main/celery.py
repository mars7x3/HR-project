import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')

app = Celery('main')
app.config_from_object('django.conf:settings')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'report_chicago_5-0': {
        'schedule': crontab(minute='*/3'),
        'task': 'vacancy.tasks.vip_vacancies_update'
    },

}

app.conf.timezone = settings.TIME_ZONE
