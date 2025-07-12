import logging

import stripe
from django.conf import settings
from django.db import transaction
from django.urls import reverse

from apps.core.tasks import send_email_notification
from apps.payments.models import Payment
from apps.tasks.models import Task

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    def create_checkout_session(self, task: Task) -> str | None:
        """
        Creates stripe checkout session,
        creates payment object if session created successfully.
        Sends Email to client of payed task.
        """

        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": task.title,
                            },
                            "unit_amount": int(task.price * 100),  # Amount in cents
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=reverse("payments:payment-success"),
                cancel_url=reverse("payments:payment-cancel"),
                client_reference_id=str(task.pk),
            )
        except stripe.StripeError as e:
            logger.error(f"Failed to create stripe session: {e}")
            return

        if not checkout_session.url:
            logger.warning(
                f"Url for checkout session for task {task.pk} wasn't created"
            )
            return

        payment = Payment.objects.create(
            task=task,
            client=task.client,
            amount=task.price,
            status=Payment.PaymentStatus.PENDING,
        )
        logger.info(
            f"Created pending payment (ID: {payment.pk}) for task ID: {task.pk}"
        )

        logger.info(f"Created stripe checkout session for task ID: {task.pk}")

        send_email_notification.delay(
            subject="Checkout session created",
            message=f"To pay task - go to link {checkout_session.url}",
            recipient_list=[task.client.email],
        )

        return checkout_session.url

    @transaction.atomic
    def handle_webhook_event(self, payload, sig_header) -> None:
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            logger.info(
                f"Successfully constructed Stripe webhook event of type: {event.type}"
            )
        except ValueError as e:
            logger.error(f"Invalid payload for Stripe webhook: {e}")
            raise e
        except stripe.SignatureVerificationError as e:
            logger.error(f"Invalid signature for Stripe webhook: {e}")
            raise e

        if event.type == "checkout.session.completed":
            session = event.data.object
            client_reference_id = session.client_reference_id
            try:
                payment = Payment.objects.get(id=client_reference_id)
                payment.status = Payment.PaymentStatus.SUCCEEDED
                payment.save()
                payment.task.pay()
                payment.task.save()
                logger.info(
                    f"Payment (ID: {payment.pk}) for task (ID: {payment.task.pk}) "
                    "succeeded."
                )
                send_email_notification.delay(
                    subject="Task paid successfully",
                    message=f"Your task {payment.task.title} was paid successfully",
                    recipient_list=[payment.task.client.email],
                )
            except Payment.DoesNotExist:
                logger.error(
                    f"Payment with client_reference_id {client_reference_id} not found."
                )
