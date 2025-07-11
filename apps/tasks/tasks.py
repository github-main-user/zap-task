from celery import shared_task
from django.utils import timezone

from .models import Task

import logging

logger = logging.getLogger(__name__)


@shared_task
def expire_tasks() -> None:
    """Expire tasks that are past their deadline."""
    now = timezone.now()
    tasks_to_expire = Task.objects.filter(
        deadline__lt=now,
        status__in=[Task.TaskStatus.OPEN, Task.TaskStatus.IN_PROGRESS],
    )
    logger.info(f"Found {tasks_to_expire.count()} tasks to expire.")
    for task in tasks_to_expire:
        task.expire()
        task.save()
        logger.info(f"Task '{task.title}' has expired.")
