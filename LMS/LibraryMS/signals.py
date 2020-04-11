from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, BookCopy


@receiver(post_save, sender=BookCopy)
def create_availability(sender, instance, created, **kwargs):
    if created:
        Book.objects.create(ISBN=instance.ISBN, availability=kwargs['availability'])


@receiver(post_save, sender=BookCopy)
def save_availability(sender, instance, **kwargs):
    instance.profile.save()
