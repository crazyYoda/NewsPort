# runapscheduler.py
import logging
from datetime import datetime

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from NewsPort1.news.models import Category, Post

logger = logging.getLogger(__name__)


def my_job():
    tags_post_dict = {}
    tags_users_dict = {}
    list_of_posts = []
    list_of_users = []
    tags_subs = {}
    for tag in Category.objects.all():
        tags_post_dict[tag.tag] = Post.objects.filter(create_time__gt= datetime.fromtimestamp(datetime.timestamp(datetime.now()) - 604800), categories=tag)
        tags_users_dict[tag.tag] = Category.objects.get(tag=tag).subscribers.all()
        list_of_posts.append(Post.objects.filter(create_time__gt= datetime.fromtimestamp(datetime.timestamp(datetime.now()) - 604800), categories=tag))


    for tag in Category.objects.all():
        posts = tags_post_dict[tag.tag]
        users = tags_users_dict[tag.tag]
        emails = []
        for user in users:
            emails.append(user.email)
        html_content = render_to_string(
            '../templates/subs_email.html',
            {
                'posts': posts, 'tag': tag.tag,
            }
        )
        msg = EmailMultiAlternatives(
            subject='Недельная рассылка новостей',
            body='',
            from_email='aiki_neru@mail.ru',
            to=emails
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()
# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after our job has run.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day="*/7"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
