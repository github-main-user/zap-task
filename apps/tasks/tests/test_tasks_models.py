import pytest
from django.contrib.auth import get_user_model

from django_fsm import TransitionNotAllowed
from apps.tasks.models import Task

User = get_user_model()


# start


@pytest.mark.django_db
def test_start_task_successfully(task_obj, freelancer_user):
    task_obj.freelancer = freelancer_user
    task_obj.save()

    task_obj.start()
    assert task_obj.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_start_task_without_freelancer_raises_exception(task_obj):
    with pytest.raises(TransitionNotAllowed):
        task_obj.start()


@pytest.mark.django_db
def test_start_task_with_invalid_status_raises_exception(task_obj, freelancer_user):
    task_obj.freelancer = freelancer_user
    task_obj.status = Task.TaskStatus.IN_PROGRESS
    task_obj.save()

    with pytest.raises(TransitionNotAllowed):
        task_obj.start()


# begin_review


@pytest.mark.django_db
def test_begin_review_successfully(task_obj, freelancer_user):
    task_obj.freelancer = freelancer_user
    task_obj.status = Task.TaskStatus.IN_PROGRESS
    task_obj.save()

    task_obj.begin_review()
    assert task_obj.status == Task.TaskStatus.PENDING_REVIEW


@pytest.mark.django_db
def test_begin_review_with_invalid_status_raises_exception(task_obj):
    task_obj.status = Task.TaskStatus.OPEN
    task_obj.save()

    with pytest.raises(TransitionNotAllowed):
        task_obj.begin_review()


# complete


@pytest.mark.django_db
def test_complete_task_successfully(task_obj):
    task_obj.status = Task.TaskStatus.PENDING_REVIEW
    task_obj.save()

    task_obj.complete()
    assert task_obj.status == Task.TaskStatus.COMPLETED


@pytest.mark.django_db
def test_complete_task_with_invalid_status_raises_exception(task_obj):
    task_obj.status = Task.TaskStatus.IN_PROGRESS
    task_obj.save()

    with pytest.raises(TransitionNotAllowed):
        task_obj.complete()


# reject


@pytest.mark.django_db
def test_reject_task_successfully(task_obj):
    task_obj.status = Task.TaskStatus.PENDING_REVIEW
    task_obj.save()

    task_obj.reject()
    assert task_obj.status == Task.TaskStatus.IN_PROGRESS


@pytest.mark.django_db
def test_reject_task_with_invalid_status_raises_exception(task_obj):
    task_obj.status = Task.TaskStatus.COMPLETED
    task_obj.save()

    with pytest.raises(TransitionNotAllowed):
        task_obj.reject()


# cancel


@pytest.mark.django_db
def test_cancel_task_successfully(task_obj):
    assert task_obj.status == Task.TaskStatus.OPEN
    task_obj.cancel()
    assert task_obj.status == Task.TaskStatus.CANCELED


@pytest.mark.django_db
def test_cancel_task_with_invalid_status_raises_exception(task_obj):
    task_obj.status = Task.TaskStatus.IN_PROGRESS
    task_obj.save()

    with pytest.raises(TransitionNotAllowed):
        task_obj.cancel()


# expire


@pytest.mark.django_db
def test_expire_task_from_open_successfully(task_obj):
    task_obj.status = Task.TaskStatus.OPEN
    task_obj.save()

    task_obj.expire()
    assert task_obj.status == Task.TaskStatus.EXPIRED


@pytest.mark.django_db
def test_expire_task_from_in_progress_successfully(task_obj):
    task_obj.status = Task.TaskStatus.IN_PROGRESS
    task_obj.save()

    task_obj.expire()
    assert task_obj.status == Task.TaskStatus.EXPIRED


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        Task.TaskStatus.PENDING_REVIEW,
        Task.TaskStatus.COMPLETED,
        Task.TaskStatus.CANCELED,
    ],
)
def test_expire_task_with_invalid_status_raises_exception(task_obj, status):
    task_obj.status = status
    task_obj.save()

    with pytest.raises(TransitionNotAllowed):
        task_obj.expire()
