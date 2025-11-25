from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from .models import Course

@receiver(m2m_changed, sender=Course.instructors.through)
def set_user_role_to_instructor(sender, instance, action, pk_set, **kwargs):
    if action == "post_add":  # Users added as instructors
        for user_id in pk_set:
            user = instance.instructors.model.objects.get(pk=user_id)
            if user.role != "instructor":
                user.role = "instructor"
                user.save()

