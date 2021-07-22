from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

import datetime
from datetime import timezone, timedelta

from .models import Post, Category


def send_by_create():
    categories = Category.objects.all()
    for category in categories:
        subject = f'Новости по подписке в категории: {category}'

        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            html_message = render_to_string(
                'news/mail_new_post_for_subscribers.html',
                {
                    'username': subscriber,
                    'site': 'http://127.0.0.1:8000',
                    'category': category
                }
            )

            send_mail(
                subject=subject,
                message="message",
                from_email='test_for_skills@mail.ru',
                recipient_list=[subscriber.email],
                html_message=html_message
            )

def send_by_week():
    global Posts, subscriber, timing, cat
    timer = datetime.now(timezone.utc)

    Userposts = {}

    for cat in Category.objects.all():
        for subscriber in cat.subscribers.all():
            my_post = Post.objects.filter(category_id=cat.id, time_in__gte=(timer - timedelta(days=7)))
            Posts = list(my_post)
            if Posts:
                Userposts[subscriber] = Userposts.get(subscriber, []) + [Posts]
    Dict = Userposts.items()
    for user, art in Dict:
        html_content = render_to_string(
            'subs_email.html',
            {
                'user': user,
                'art': art,
            }
        )
        msg = EmailMultiAlternatives(
            subject='Weekly posts',
            from_email='test_for_skills@mail.ru',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

