from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("task", "reviewer", "recipient", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("task__title", "reviewer__email", "recipient__email", "comment")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
