from apps.core.tasks import send_email_task
from apps.users.models import User

from .models import Task


def start_task(task: Task) -> None:
    """
    Starts a task and sends an email notification.
    """
    task.start()
    task.save()
    send_email_task.delay(
        subject="Task Started",
        message=f"Task '{task.title}' was started by {task.freelancer}.",
        recipient_list=[task.client.email],
    )


def submit_task(task: Task) -> None:
    """
    Submits a task for review and sends an email notification.
    """
    task.begin_review()
    task.save()
    send_email_task.delay(
        subject="Task Submitted",
        message=f"Task '{task.title}' was submitted by {task.freelancer}.",
        recipient_list=[task.client.email],
    )


def approve_task_submission(task: Task) -> None:
    """
    Approves a task submission and sends an email notification.
    """
    task.complete()
    task.save()
    send_email_task.delay(
        subject="Task Approved",
        message=f"Task '{task.title}' was approved by {task.client}.",
        recipient_list=[task.freelancer.email],
    )


def reject_task_submission(task: Task) -> None:
    """
    Rejects a task submission and sends an email notification.
    """
    task.reject()
    task.save()
    send_email_task.delay(
        subject="Task Rejected",
        message=f"Task '{task.title}' was rejected by {task.client}.",
        recipient_list=[task.freelancer.email],
    )


def cancel_task(task: Task, user: User) -> None:
    """
    Cancels a task and sends an email notification.
    """
    task.cancel()
    task.save()

    if user == task.client:
        recipient_list = [task.freelancer.email]
        message = f"Task '{task.title}' was canceled by the client."
    else:
        recipient_list = [task.client.email]
        message = f"Task '{task.title}' was canceled by the freelancer."

    send_email_task.delay(
        subject="Task Canceled",
        message=message,
        recipient_list=recipient_list,
    )
