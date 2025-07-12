from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "freelancer", "status", "price", "deadline")
    list_filter = ("status", "deadline")
    search_fields = ("title", "description", "client__email", "freelancer__email")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
