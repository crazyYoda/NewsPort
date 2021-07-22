import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NewsPort1.settings')

app = Celery('NewsPort1')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'weekly_posts_for_subscribers': {
        'task': 'tasks.weekly_posts',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
    },
}