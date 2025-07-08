from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = (
            "id",
            "task",
            "reviewer",
            "recipient",
            "rating",
            "comment",
            "created_at",
        )
        read_only_fields = ("task", "reviewer", "recipient", "created_at")

    def validate(self, attrs):
        if self.instance is None:  # validation only on create
            task = self.context["task"]
            request = self.context["request"]
            if Review.objects.filter(task=task, reviewer=request.user).exists():
                raise serializers.ValidationError(
                    "You've already submitted a review for this task."
                )
        return attrs
