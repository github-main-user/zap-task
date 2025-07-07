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
        if self.instance is None:  # validation only on create
            task = self.context["task"]
            freelancer = self.context["freelancer"]

            if Proposal.objects.filter(task=task, freelancer=freelancer).exists():
                raise serializers.ValidationError(
                    "You've already submitted a proposal for this task."
                )

            attrs |= {"task": task, "freelancer": freelancer}

        return attrs
