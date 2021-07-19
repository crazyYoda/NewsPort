from django.core.mail import send_mail
from django.db.models.signals import m2m_changed
from django.dispatch import receiver # импортируем нужный декоратор
from django.template.loader import render_to_string

from .models import Post


@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_subscribers(sender, instance, **kwargs):
    categories = instance.postCategory.all()
    for category in categories:
        subject = f'Новости по подписке в категории: {category}'

        subscribers = category.subscribers.all()
        for subscriber in subscribers:
            html_message = render_to_string(
                'news/mail_new_post_for_subscribers.html',
                {
                    'username': subscriber,
                    'post': instance,
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

# @receiver(m2m_changed, sender=Post.postCategory.through)
# def notify_users(sender, instance, **kwargs):
#     action = kwargs['action']
#     if action == 'post_add':
#         categories = instance.postCategory.all()
#         for category in categories:
#             subject = f'Новая статья в категории {category}'
#             subscribers = category.subscribers.all()
#             for subscriber in subscribers:
#                 html_content = render_to_string(
#                     'news/mail_new_post_for_subscribers.html',
#                     {
#                         'username': subscriber,
#                         'post': instance,
#                         'site': 'http://127.0.0.1:8000',
#                     }
#                 )
#                 msg = EmailMultiAlternatives(
#                     subject=subject,
#                     from_email='aiki_neru@mail.ru',
#                     to=[subscriber.email],
#                 )
#                 msg.attach_alternative(html_content, "text/html")
#                 msg.send()