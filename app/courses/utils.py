import cloudinary
import cloudinary.uploader


from app.courses.models import Lesson, UserLessonCompletion, Course
from rest_framework.exceptions import PermissionDenied



from django.utils import timezone
from django.utils.timesince import timesince
from datetime import timedelta
from rest_framework.exceptions import PermissionDenied
from app.courses.models import Lesson, UserLessonCompletion


def get_user_lessons(user):
    pass


def get_completed_level(user, course):
    lessons = get_user_lessons(user).filter(course=course)
    total_lessons = lessons.count()
    if total_lessons == 0:
        return 0

    completed = UserLessonCompletion.objects.filter(user=user, lesson__in=lessons).count()
    return round((completed / total_lessons) * 100, 2)


def lesson_permission(lesson, user):
    previous_lessons = Lesson.objects.filter(
        course=lesson.course,
        order__lt=lesson.order
    ).order_by("order")

    allowed_lessons = set(get_user_lessons(user))

    for prev in previous_lessons:
        if prev not in allowed_lessons:
            raise PermissionDenied(
                f"You do not have access to lesson {prev.order} - {prev.title}."
            )

        try:
            completion = UserLessonCompletion.objects.get(user=user, lesson=prev)
        except UserLessonCompletion.DoesNotExist:
            raise PermissionDenied(
                f"You must complete lesson {prev.order} - {prev.title} before accessing this one."
            )

    return True