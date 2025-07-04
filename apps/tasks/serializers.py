from django.utils import timezone
from rest_framework import serializers

from apps.users.serializers import UserShortSerializer

from .models import Proposal, Task


class TaskSerializer(serializers.ModelSerializer):
    client = UserShortSerializer(read_only=True)
    freelancer = UserShortSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "price",
            "deadline",
            "status",
            "client",
            "freelancer",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "status",
            "client",
            "freelancer",
            "created_at",
            "updated_at",
        )

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Deadline must be in the future.")
        return value


class ProposalSerializer(serializers.ModelSerializer):
    freelancer = UserShortSerializer(read_only=True)
    task = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Proposal
        fields = (
            "id",
            "task",
            "freelancer",
            "message",
            "price_offer",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "freelancer", "task", "status", "created_at")
