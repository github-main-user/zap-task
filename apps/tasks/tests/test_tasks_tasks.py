from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tasks.models import Task
from apps.tasks.tasks import expire_tasks


@pytest.mark.django_db
def test_expire_tasks_expires_open_and_in_progress_tasks(task_factory):
    yesterday = timezone.now() - timedelta(days=1)
    tomorrow = timezone.now() + timedelta(days=1)

    # Tasks that should expire
    task_factory(deadline=yesterday, status=Task.TaskStatus.OPEN)
    task_factory(deadline=yesterday, status=Task.TaskStatus.IN_PROGRESS)

    # Tasks that should not expire
    task_factory(deadline=tomorrow, status=Task.TaskStatus.OPEN)
    task_factory(deadline=yesterday, status=Task.TaskStatus.COMPLETED)
    task_factory(deadline=yesterday, status=Task.TaskStatus.EXPIRED)

    expire_tasks()

    expired_tasks = Task.objects.filter(status=Task.TaskStatus.EXPIRED)
    assert expired_tasks.count() == 3

    for task in expired_tasks:
        assert task.deadline < timezone.now()
        assert task.status == Task.TaskStatus.EXPIRED
