from django.db.models.signals import post_save
from django.contrib.auth.models import User
from project.backend.models import userProfile


def createUserProfile(sender, instance, created, **kwargs):
    """Create a UserProfile object each time a User is created ; and link it.
    """
    if created:
        try:
            a = userProfile.objects.get_or_create(user=instance)
            last_name = instance.last_name
            first_name = instance.first_name
            a[0].first_name = first_name
            a[0].last_name = last_name
            a[0].save()
        except:
            pass


post_save.connect(createUserProfile, sender=User)
