from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("task", "client", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("task__title", "client__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
