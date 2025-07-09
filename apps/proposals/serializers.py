from rest_framework import serializers

from .models import Proposal


class ProposalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proposal
        fields = (
            "id",
            "task",
            "freelancer",
            "message",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("task", "freelancer", "status", "created_at", "updated_at")

    def validate(self, attrs):
        """
        Validates that one user can have only one proposal per task.
        Validates it only on create.
        After validation task and freelancer objects being saved to attributes.
        """

        if self.instance is None:
            task = self.context["task"]
            freelancer = self.context["freelancer"]

            if Proposal.objects.filter(task=task, freelancer=freelancer).exists():
                raise serializers.ValidationError(
                    "You've already submitted a proposal for this task."
                )

            attrs |= {"task": task, "freelancer": freelancer}

        return attrs
