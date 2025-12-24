from core.models import (
    Assesment,
    AssessmentLearningOutcome,
    Course,
    LearningOutcome,
    ProgramLearningOutcome,
    ProgramOutcome,
    User,
)
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class TeacherCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=25)
    email = serializers.EmailField()

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email already taken")
        return value

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password("dionysos"),
            role="teacher",
            is_staff=True,
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance


class StudentCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=25)
    email = serializers.EmailField()

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email already taken")
        return value

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password("dionysos"),
            role="student",
            is_staff=False,
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance


class HeadUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=25)
    email = serializers.EmailField(validators=[validate_email])
    password = serializers.CharField(min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            role="head",
            is_superuser=True,
            is_staff=True,
        )
        return user


class ProgramOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramOutcome
        fields = ["code", "description"]


class ProgramOutcomeCreateSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=25)
    description = serializers.CharField(max_length=500)

    def validate_code(self, value):
        qs = ProgramOutcome.objects.filter(code=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Code already taken.")
        return value

    def create(self, validated_data):
        return ProgramOutcome.objects.create(
            code=validated_data["code"],
            description=validated_data["description"],
        )

    def update(self, instance, validated_data):
        instance.code = validated_data.get("code", instance.code)
        instance.description = validated_data.get("description", instance.description)
        instance.save()
        return instance


class ProgramLearningOutcomeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    weight = serializers.IntegerField(min_value=1, max_value=5)


class LearningOutcomeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)
    description = serializers.CharField()
    program_outcomes = ProgramLearningOutcomeSerializer(many=True)


class AssessmentLearningOutcomeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=20)
    weight = serializers.IntegerField(min_value=1, max_value=5)


class AssessmentSerializer(serializers.Serializer):
    assessment_type = serializers.ChoiceField(
        choices=[("midterm", "Midterm"), ("project", "Project"), ("final", "Final")]
    )
    learning_outcomes = AssessmentLearningOutcomeSerializer(many=True)


class CourseSummarySerializer(serializers.ModelSerializer):
    course_code = serializers.CharField(source="code")
    course_name = serializers.CharField(source="name")
    created_by = serializers.SerializerMethodField()
    learning_outcome_count = serializers.IntegerField(
        source="learning_outcomes.count", read_only=True
    )
    assessment_count = serializers.IntegerField(
        source="assesments.count", read_only=True
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "course_code",
            "course_name",
            "created_by",
            "learning_outcome_count",
            "assessment_count",
        ]

    def get_created_by(self, obj):
        if obj.created_by:
            return {"username": obj.created_by.username}
        return {"username": "Unknown"}


class CourseCreateSerializer(serializers.Serializer):
    course_code = serializers.CharField(max_length=10)
    course_name = serializers.CharField(max_length=100)
    learning_outcomes = LearningOutcomeSerializer(many=True)
    assessments = AssessmentSerializer(many=True, required=False)

    def create(self, validated_data):
        user = self.context["request"].user
        learning_outcomes_data = validated_data.pop("learning_outcomes", [])
        assessments_data = validated_data.pop("assessments", [])

        course = Course.objects.create(
            code=validated_data["course_code"],
            name=validated_data["course_name"],
            created_by=user,
        )

        lo_objects = []
        for lo_data in learning_outcomes_data:
            program_outcomes_data = lo_data.pop("program_outcomes", [])
            lo = LearningOutcome.objects.create(
                code=lo_data["code"],
                description=lo_data["description"],
                course=course,
                created_by=user,
            )

            for po_data in program_outcomes_data:
                try:
                    po = ProgramOutcome.objects.get(code=po_data["code"])
                except ProgramOutcome.DoesNotExist:
                    continue  # veya hata fırlatabilirsiniz
                ProgramLearningOutcome.objects.create(
                    learning_outcome=lo,
                    program_outcome=po,
                    weight=po_data["weight"],
                )

            lo_objects.append(lo)

        for a_data in assessments_data:
            assessment = Assesment.objects.create(
                name=a_data["assessment_type"],
                course=course,
                created_by=user,
            )
            for lo_info in a_data["learning_outcomes"]:
                lo_code = lo_info["code"]
                weight = lo_info["weight"]
                try:
                    lo = LearningOutcome.objects.get(code=lo_code, course=course)
                except LearningOutcome.DoesNotExist:
                    continue
                AssessmentLearningOutcome.objects.create(
                    assesment=assessment, learning_outcome=lo, weight=weight
                )

        return course
