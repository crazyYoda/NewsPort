from NewsPort1.celery import app

from celery import shared_task

from .service import send_by_create, send_by_week


@app.task
def send_email_for_subscribers():
    send_by_create()


@shared_task
def weekly_posts():
    send_by_week()