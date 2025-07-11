from unittest.mock import MagicMock, patch

import pytest
import stripe

from apps.payments.models import Payment
from apps.payments.services import StripeService
from apps.tasks.models import Task


@pytest.fixture
def mock_stripe():
    with patch("stripe.checkout.Session.create") as mock_create:
        with patch("stripe.Webhook.construct_event") as mock_construct_event:
            yield mock_create, mock_construct_event


@pytest.mark.django_db
def test_create_checkout_session_success(mock_stripe, task_factory):
    mock_create, _ = mock_stripe
    mock_create.return_value.url = "http://mock-stripe-url.com"
    task = task_factory()
    service = StripeService()

    checkout_url = service.create_checkout_session(task)

    assert checkout_url == "http://mock-stripe-url.com"
    mock_create.assert_called_once()
    payment = Payment.objects.get(task=task, client=task.client)
    assert payment.amount == task.price
    assert payment.status == Payment.PaymentStatus.PENDING


@pytest.mark.django_db
def test_create_checkout_session_stripe_error(mock_stripe, task_factory):
    mock_create, _ = mock_stripe
    mock_create.side_effect = stripe.StripeError("Stripe error")
    task = task_factory()
    service = StripeService()

    checkout_url = service.create_checkout_session(task)

    assert checkout_url is None
    mock_create.assert_called_once()
    assert not Payment.objects.filter(task=task).exists()


@pytest.mark.django_db
def test_handle_webhook_event_checkout_session_completed_success(
    mock_stripe, payment_factory
):
    _, mock_construct_event = mock_stripe
    payment = payment_factory()
    mock_construct_event.return_value = MagicMock(
        type="checkout.session.completed",
        data=MagicMock(
            object=MagicMock(
                client_reference_id=str(payment.id),
            )
        ),
    )

    service = StripeService()
    service.handle_webhook_event("payload", "sig_header")

    payment.refresh_from_db()
    assert payment.status == Payment.PaymentStatus.SUCCEEDED
    assert payment.task.status == Task.TaskStatus.PAID


@pytest.mark.django_db
def test_handle_webhook_event_checkout_session_completed_payment_not_found(
    mock_stripe,
):
    _, mock_construct_event = mock_stripe
    mock_construct_event.return_value = MagicMock(
        type="checkout.session.completed",
        data=MagicMock(
            object=MagicMock(
                client_reference_id="99999",  # Non-existent payment ID
            )
        ),
    )

    service = StripeService()
    service.handle_webhook_event("payload", "sig_header")


@pytest.mark.django_db
def test_handle_webhook_event_charge_refunded(mock_stripe):
    _, mock_construct_event = mock_stripe
    mock_construct_event.return_value = MagicMock(
        type="charge.refunded",
        data=MagicMock(
            object=MagicMock(
                id="refund_id",
            )
        ),
    )

    service = StripeService()
    service.handle_webhook_event("payload", "sig_header")


@pytest.mark.django_db
def test_handle_webhook_event_invalid_payload(mock_stripe):
    _, mock_construct_event = mock_stripe
    mock_construct_event.side_effect = ValueError("Invalid payload")

    service = StripeService()
    with pytest.raises(ValueError):
        service.handle_webhook_event("payload", "sig_header")


@pytest.mark.django_db
def test_handle_webhook_event_invalid_signature(mock_stripe):
    _, mock_construct_event = mock_stripe
    mock_construct_event.side_effect = Exception("Invalid signature")

    service = StripeService()
    with pytest.raises(Exception):
        service.handle_webhook_event("payload", "sig_header")
