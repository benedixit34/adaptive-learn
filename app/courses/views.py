from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Subquery


from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action


from app.courses.permissions import CanAccessLesson, CanEnroll


from .models import (
    Course,
    Lesson,
    UserLessonCompletion,
)
from .serializers import (
    CourseReadSerializer,
    CourseWriteSerializer,
    LessonListReadSerializer,
    LessonRetrieveReadSerializer,
    LessonWriteSerializer,
    UserLessonCompletionSerializer,
)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    lookup_field = "uuid"

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = serializer.save()
        read_serializer = CourseReadSerializer(course)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return Course.objects.prefetch_related("instructors").all()


    @action(detail=True, methods=['get'], url_path="lessons/completed")
    def completed_lessons(self, request, uuid=None):
        course = self.get_object()
        user = request.user

        completed_ids = (
            UserLessonCompletion.objects
            .filter(user=user, lesson__course=course)
            .values_list('lesson_id', flat=True)
        )

        completed_lessons = Lesson.objects.filter(id__in=completed_ids).order_by("order")
        completed_lessons = completed_lessons.select_related('course', 'section')
        serializer = LessonListReadSerializer(completed_lessons, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

            
    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated, IsAdminUser]

        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return CourseReadSerializer
        return CourseWriteSerializer


class LessonViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"

    def get_queryset(self):
        course_uuid = self.kwargs.get("course_uuid")
        course = get_object_or_404(Course, uuid=course_uuid)
        return course.lessons.all()

    
    def get_permissions(self):
        if self.action in ["list"]:
            self.permission_classes = [IsAuthenticated]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAdminUser]
        elif self.action in ["retrieve", "complete_lesson"]:
            self.permission_classes = [IsAuthenticated, CanAccessLesson]
        else:
            self.permission_classes = [IsAdminUser]
        return [perm() for perm in self.permission_classes]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return LessonListReadSerializer
        elif self.action in ["retrieve"]:
            return LessonRetrieveReadSerializer
        return LessonWriteSerializer

    def create(self, request, course_uuid):
        request.data["course"] = course_uuid
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            course = serializer.validated_data["course"]
            order = course.lessons.count() + 1
            serializer.validated_data["order"] = order
            lesson = serializer.save()
        read_serializer = LessonRetrieveReadSerializer(lesson)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    
    #Add complete Lesson Endpoint
    @action(detail=True, methods=["post"], url_path="completed")
    def complete_lesson(self, request, *args, **kwargs):
        lesson = self.get_object()
        user_completion, created = UserLessonCompletion.objects.update_or_create(
            user=self.request.user,
            lesson=lesson,
            defaults={}
        )
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        serializer = UserLessonCompletionSerializer(user_completion)
        return Response(serializer.data, status=status_code)

