from django.utils import timezone
from rest_framework import serializers

from .models import Proposal, Task


class TaskSerializer(serializers.ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(read_only=True)
    freelancer = serializers.PrimaryKeyRelatedField(read_only=True)

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
    freelancer = serializers.PrimaryKeyRelatedField(read_only=True)
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
        read_only_fields = ("id", "task", "freelancer", "status", "created_at")

    def validate(self, attrs):
        if self.instance is None:  # validation only on create
            task = self.context["task"]
            freelancer = self.context["freelancer"]

            if Proposal.objects.filter(task=task, freelancer=freelancer).exists():
                raise serializers.ValidationError(
                    "You've already submitted a proposal for this task."
                )

            attrs |= {"task": task, "freelancer": freelancer}

        return attrs
