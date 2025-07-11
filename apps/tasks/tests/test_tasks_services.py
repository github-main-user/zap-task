from unittest.mock import patch

import pytest

from apps.tasks import services
from apps.tasks.models import Task


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_start_task(mock_send_email_notification, task_factory, freelancer_user):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.PAID)

    services.start_task(task)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.IN_PROGRESS
    mock_send_email_notification.assert_called_once()


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_pay_task(mock_send_email_notification, task_factory, freelancer_user):
    task = task_factory(freelancer=freelancer_user)

    services.pay_task(task)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.PAID
    mock_send_email_notification.assert_called_once()


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_submit_task(mock_send_email_notification, task_factory, freelancer_user):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS, freelancer=freelancer_user)

    services.submit_task(task)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.PENDING_REVIEW
    mock_send_email_notification.assert_called_once()


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_approve_task_submission(
    mock_send_email_notification, task_factory, freelancer_user
):
    task = task_factory(
        status=Task.TaskStatus.PENDING_REVIEW, freelancer=freelancer_user
    )

    services.approve_task_submission(task)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.COMPLETED
    mock_send_email_notification.assert_called_once()


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_reject_task_submission(
    mock_send_email_notification, task_factory, freelancer_user
):
    task = task_factory(
        status=Task.TaskStatus.PENDING_REVIEW, freelancer=freelancer_user
    )

    services.reject_task_submission(task)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.IN_PROGRESS
    mock_send_email_notification.assert_called_once()


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_cancel_task_as_client(
    mock_send_email_notification, task_factory, freelancer_user
):
    task = task_factory(freelancer=freelancer_user)

    services.cancel_task(task, task.client)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.CANCELED
    mock_send_email_notification.assert_called_once()


@pytest.mark.django_db
@patch("apps.tasks.services.send_email_notification.delay")
def test_cancel_task_as_freelancer(
    mock_send_email_notification, task_factory, freelancer_user
):
    task = task_factory(freelancer=freelancer_user)

    services.cancel_task(task, task.freelancer)

    task.refresh_from_db()
    assert task.status == Task.TaskStatus.CANCELED
    mock_send_email_notification.assert_called_once()
