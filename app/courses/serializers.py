from cloudinary_storage.validators import validate_video
from rest_framework import serializers


from .models import Course, Lesson, UserLessonCompletion, UserCourseProgress

class CourseWriteSerializer(serializers.ModelSerializer):
    instructors = serializers.PrimaryKeyRelatedField(
        queryset=Instructor.objects.all(), many=True
    )

    class Meta:
        model = Course
        fields = ["name", "description", "language", "instructors"]

    def create(self, validated_data):
        instructors = validated_data.pop("instructors", [])
        course = Course.objects.create(**validated_data)
        course.instructors.set(instructors)
        return course


class CourseReadSerializer(serializers.ModelSerializer):
    instructors = InstructorReadSerializer(many=True)

    class Meta:
        model = Course
        fields = [
            "uuid",
            "name",
            "description",
            "language",
        ]

   


class LessonWriteSerializer(serializers.ModelSerializer):
    course = serializers.UUIDField(write_only=True)

    class Meta:
        model = Lesson
        fields = [
            "course",
            "title",
            "description",
        ]

    def validate_course(self, value):
        try:
            return Course.objects.get(uuid=value)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course with this UUID does not exist.")

    def create(self, validated_data):
        course = validated_data.pop("course")
        lesson = Lesson.objects.create(course=course, **validated_data)
        return lesson


class VideoReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["uuid", "name", "description", "video", "featured_image"]


class LessonRetrieveReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = [
            "uuid",
            "title",
            "description",
            "order",
            "video",
        ]

class LessonListReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "uuid",
            "title",
            "description",
            "order",
        ]



class UserLessonCompletionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())

    class Meta:
        model = UserLessonCompletion
        fields = ['user', 'lesson']






