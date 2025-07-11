import pytest
from django.contrib.auth import get_user_model
from django_fsm import TransitionNotAllowed

from apps.tasks.models import Task

User = get_user_model()


# start


@pytest.mark.django_db
def test_start_task_successfully(freelancer_user, task_factory):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.PAID)
    task.start()

    assert task.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_start_task_without_freelancer_raises_exception(task_factory):
    task = task_factory(status=Task.TaskStatus.PAID)

    with pytest.raises(TransitionNotAllowed):
        task.start()


@pytest.mark.django_db
def test_pay_task_successfully(task_factory, freelancer_user):
    task = task_factory(freelancer=freelancer_user)
    task.pay()

    assert task.status == Task.TaskStatus.PAID


@pytest.mark.django_db
def test_pay_task_with_invalid_status_raises_exception(task_factory):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)

    with pytest.raises(TransitionNotAllowed):
        task.pay()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        Task.TaskStatus.OPEN,
        Task.TaskStatus.IN_PROGRESS,
        Task.TaskStatus.PENDING_REVIEW,
        Task.TaskStatus.COMPLETED,
        Task.TaskStatus.CANCELED,
        Task.TaskStatus.EXPIRED,
    ],
)
def test_start_task_with_invalid_status_raises_exception(freelancer_user, task_factory, status):
    task = task_factory(freelancer=freelancer_user, status=status)

    with pytest.raises(TransitionNotAllowed):
        task.start()


# begin_review


@pytest.mark.django_db
def test_begin_review_successfully(freelancer_user, task_factory):
    task = task_factory(freelancer=freelancer_user, status=Task.TaskStatus.IN_PROGRESS)
    task.begin_review()

    assert task.status == Task.TaskStatus.PENDING_REVIEW


@pytest.mark.django_db
def test_begin_review_with_invalid_status_raises_exception(task_factory):
    task = task_factory()

    with pytest.raises(TransitionNotAllowed):
        task.begin_review()


# complete


@pytest.mark.django_db
def test_complete_task_successfully(task_factory):
    task = task_factory(status=Task.TaskStatus.PENDING_REVIEW)
    task.complete()

    assert task.status == Task.TaskStatus.COMPLETED


@pytest.mark.django_db
def test_complete_task_with_invalid_status_raises_exception(task_factory):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)

    with pytest.raises(TransitionNotAllowed):
        task.complete()


# reject


@pytest.mark.django_db
def test_reject_task_successfully(task_factory):
    task = task_factory(status=Task.TaskStatus.PENDING_REVIEW)
    task.reject()

    assert task.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_reject_task_with_invalid_status_raises_exception(task_factory):
    task = task_factory(status=Task.TaskStatus.COMPLETED)

    with pytest.raises(TransitionNotAllowed):
        task.reject()


# cancel


@pytest.mark.django_db
def test_cancel_task_successfully(task_factory):
    task = task_factory()
    task.cancel()

    assert task.status == Task.TaskStatus.CANCELED


@pytest.mark.django_db
def test_cancel_task_with_invalid_status_raises_exception(task_factory):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)

    with pytest.raises(TransitionNotAllowed):
        task.cancel()


# expire


@pytest.mark.django_db
def test_expire_task_from_open_successfully(task_factory):
    task = task_factory()
    task.expire()

    assert task.status == Task.TaskStatus.EXPIRED


@pytest.mark.django_db
def test_expire_task_from_in_progress_successfully(task_factory):
    task = task_factory(status=Task.TaskStatus.IN_PROGRESS)

    task.expire()
    assert task.status == Task.TaskStatus.EXPIRED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        Task.TaskStatus.PENDING_REVIEW,
        Task.TaskStatus.COMPLETED,
        Task.TaskStatus.CANCELED,
    ],
)
def test_expire_task_with_invalid_status_raises_exception(task_factory, status):
    task = task_factory(status=status)

    with pytest.raises(TransitionNotAllowed):
        task.expire()
