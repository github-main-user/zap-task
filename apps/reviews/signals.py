from django.db.models import Avg
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Review


@receiver(post_save, sender=Review)
def update_user_average_rating(sender, instance, created, **kwargs):
    if created:
        recipient = instance.recipient
        average_rating = recipient.received_reviews.aggregate(Avg("rating"))[
            "rating__avg"
        ]
        recipient.average_rating = average_rating
        recipient.save()
