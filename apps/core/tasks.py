
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email_task(subject, message, recipient_list):
    """Sends an email to a list of recipients."""
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
