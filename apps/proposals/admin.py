
from django.contrib import admin
from .models import Proposal

@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("task", "freelancer", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("task__title", "freelancer__email", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
