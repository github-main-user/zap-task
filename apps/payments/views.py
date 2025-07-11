import logging

import stripe
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.services import StripeService

logger = logging.getLogger(__name__)


class PaymentSuccessView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Payment successful!")


class PaymentCancelView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("Payment cancelled.")


@extend_schema(tags=["Payments"])
@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    @extend_schema(summary="Webhook for stripe")
    def post(self, request, *args, **kwargs):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        stripe_service = StripeService()
        try:
            stripe_service.handle_webhook_event(payload, sig_header)
            logger.info("Stripe webhook event successfully processed.")
        except ValueError as e:
            logger.error(f"Invalid payload for Stripe webhook: {e}")
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except stripe.SignatureVerificationError as e:
            logger.error(f"Invalid signature for Stripe webhook: {e}")
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error processing Stripe webhook event: {e}", exc_info=True)
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(status=status.HTTP_200_OK)
