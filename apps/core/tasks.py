import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def send_email_notification(subject, message, recipient_list) -> None:
    """Sends an email to a list of recipients with logging and retry logic."""

    logger.info(
        f"Attempting to send email to {recipient_list} with subject: '{subject}'"
    )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)
        logger.info(f"Successfully sent email to {recipient_list}.")
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_list}. Error: {e}")
        raise
