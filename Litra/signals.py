from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import RecentlyUpdate, Works, Writers, Quizz, Facts


@receiver(post_save, sender=Works)
@receiver(post_save, sender=Writers)
@receiver(post_save, sender=Quizz)
@receiver(post_save, sender=Facts)
def update_recently(sender, instance, created, **kwargs):
    if created:
        RecentlyUpdate.objects.create(content_object=instance)
