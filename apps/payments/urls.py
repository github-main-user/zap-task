from django.urls import path

from apps.payments.views import PaymentCancelView, PaymentSuccessView, StripeWebhookView

app_name = "payments"

urlpatterns = [
    path("webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
    path("success/", PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", PaymentCancelView.as_view(), name="payment-cancel"),
]
