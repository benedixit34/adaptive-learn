from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from app.general.models import CreatedUpdated

User = get_user_model()


class Course(CreatedUpdated):
    name = models.CharField(max_length=100)
    description = models.TextField()
    language = models.CharField(max_length=50)
    instructors = models.ManyToManyField(User, related_name="courses")

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["-created_at"]



class Lesson(CreatedUpdated):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField()
    video = models.URLField(max_length=250)
    featured_image = models.URLField(max_length=250)    

    def __str__(self):
        return f"{self.title}-{self.course.name}"

    class Meta:
        ordering = ["order"]


class UserLessonCompletion(CreatedUpdated):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'lesson')

    def __str__(self):
        return f"{self.user.email} has completed {self.lesson.title}"