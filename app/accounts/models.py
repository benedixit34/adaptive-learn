import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .manager import UserManager

class CustomUser(AbstractUser):
    username = None
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    course = models.ForeignKey("courses.Course", on_delete=models.SET_NULL, null=True, blank=True)
    profile_picture = models.URLField()
    role = models.CharField(max_length=15, choices=[("student", "Student"), ("instructor", "Instructor")], default="student")

    objects = UserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []


