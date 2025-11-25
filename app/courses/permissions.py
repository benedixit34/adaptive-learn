from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission
from app.courses.utils import lesson_permission


class CanAccessLesson(BasePermission):
    def has_object_permission(self, request, view, obj):
        return lesson_permission(lesson=obj, user=request.user)


class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return User.objects.filter(email=request.user.email, role="INSTRUCTOR").exists()
