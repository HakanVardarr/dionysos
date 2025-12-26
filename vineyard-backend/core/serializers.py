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

# -------------------- USER SERIALIZERS --------------------


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


# -------------------- PROGRAM OUTCOMES --------------------


class ProgramOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgramOutcome
        fields = ["id", "code", "description"]


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
    code = serializers.CharField(source="program_outcome.code")
    weight = serializers.IntegerField(min_value=1, max_value=5)


# -------------------- LEARNING OUTCOMES --------------------


class LearningOutcomeSerializer(serializers.Serializer):
    code = serializers.CharField()
    description = serializers.CharField()
    program_outcomes = ProgramLearningOutcomeSerializer(
        many=True, source="programlearningoutcome_set"
    )


# -------------------- ASSESSMENTS --------------------


class AssessmentLearningOutcomeSerializer(serializers.Serializer):
    code = serializers.CharField(source="learning_outcome.code")
    weight = serializers.IntegerField(min_value=1, max_value=5)


class AssessmentSerializer(serializers.Serializer):
    assessment_type = serializers.ChoiceField(
        choices=[
            ("midterm", "Midterm"),
            ("project", "Project"),
            ("final", "Final"),
            ("assignment", "Assignment"),
        ]
    )
    learning_outcomes = AssessmentLearningOutcomeSerializer(many=True)


# -------------------- COURSE SERIALIZERS --------------------


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
    course_code = serializers.CharField(max_length=10, source="code")
    course_name = serializers.CharField(max_length=100, source="name")
    learning_outcomes = LearningOutcomeSerializer(many=True)
    assessments = AssessmentSerializer(many=True, required=False)

    def create(self, validated_data):
        user = self.context["request"].user
        learning_outcomes_data = validated_data.pop("learning_outcomes", [])
        assessments_data = validated_data.pop("assessments", [])

        course = Course.objects.create(
            **validated_data,  # code ve name
            created_by=user,
        )

        # Learning Outcomes
        for lo_data in learning_outcomes_data:
            program_outcomes_data = lo_data.pop("programlearningoutcome_set", [])
            lo = LearningOutcome.objects.create(
                code=lo_data["code"],
                description=lo_data["description"],
                course=course,
                created_by=user,
            )
            for po_data in program_outcomes_data:
                try:
                    po = ProgramOutcome.objects.get(
                        code=po_data["program_outcome"]["code"]
                    )
                except ProgramOutcome.DoesNotExist:
                    continue
                ProgramLearningOutcome.objects.create(
                    learning_outcome=lo, program_outcome=po, weight=po_data["weight"]
                )

        # Assessments
        for a_data in assessments_data:
            assessment = Assesment.objects.create(
                name=a_data["assessment_type"],
                course=course,
                created_by=user,
            )
            for lo_info in a_data["learning_outcomes"]:
                try:
                    lo = LearningOutcome.objects.get(
                        code=lo_info["learning_outcome"]["code"], course=course
                    )
                except LearningOutcome.DoesNotExist:
                    continue
                AssessmentLearningOutcome.objects.create(
                    assesment=assessment, learning_outcome=lo, weight=lo_info["weight"]
                )

        return course

    def update(self, instance, validated_data):
        user = self.context["request"].user
        learning_outcomes_data = validated_data.pop("learning_outcomes", [])
        assessments_data = validated_data.pop("assessments", [])

        instance.code = validated_data.get("code", instance.code)
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        # Learning Outcomes
        incoming_lo_codes = [lo_data["code"] for lo_data in learning_outcomes_data]
        for lo in instance.learning_outcomes.all():
            if lo.code not in incoming_lo_codes:
                lo.delete()

        for lo_data in learning_outcomes_data:
            program_outcomes_data = lo_data.pop("programlearningoutcome_set", [])
            lo, _ = LearningOutcome.objects.update_or_create(
                code=lo_data["code"],
                course=instance,
                defaults={"description": lo_data["description"], "created_by": user},
            )
            ProgramLearningOutcome.objects.filter(learning_outcome=lo).delete()
            for po_data in program_outcomes_data:
                try:
                    po = ProgramOutcome.objects.get(
                        code=po_data["program_outcome"]["code"]
                    )
                except ProgramOutcome.DoesNotExist:
                    continue
                ProgramLearningOutcome.objects.create(
                    learning_outcome=lo, program_outcome=po, weight=po_data["weight"]
                )

        # Assessments
        existing_assessments = {a.name: a for a in instance.assesments.all()}
        for a_data in assessments_data:
            a_name = a_data["assessment_type"]
            assessment = existing_assessments.pop(a_name, None)
            if not assessment:
                assessment = Assesment.objects.create(
                    name=a_name, course=instance, created_by=user
                )
            else:
                assessment.save()

            AssessmentLearningOutcome.objects.filter(assesment=assessment).delete()
            for lo_info in a_data["learning_outcomes"]:
                try:
                    lo = LearningOutcome.objects.get(
                        code=lo_info["learning_outcome"]["code"], course=instance
                    )
                except LearningOutcome.DoesNotExist:
                    continue
                AssessmentLearningOutcome.objects.create(
                    assesment=assessment, learning_outcome=lo, weight=lo_info["weight"]
                )

        for remaining in existing_assessments.values():
            remaining.delete()

        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


# -------------------- DETAIL SERIALIZERS --------------------


class ProgramLearningOutcomeDetailSerializer(serializers.ModelSerializer):
    program_outcome = serializers.CharField(source="program_outcome.code")
    weight = serializers.IntegerField()

    class Meta:
        model = ProgramLearningOutcome
        fields = ["program_outcome", "weight"]


class LearningOutcomeDetailSerializer(serializers.ModelSerializer):
    program_outcomes = ProgramLearningOutcomeDetailSerializer(
        many=True, source="programlearningoutcome_set"
    )

    class Meta:
        model = LearningOutcome
        fields = ["code", "description", "program_outcomes"]


class AssessmentLearningOutcomeDetailSerializer(serializers.ModelSerializer):
    learning_outcome = serializers.CharField(source="learning_outcome.code")
    weight = serializers.IntegerField()

    class Meta:
        model = AssessmentLearningOutcome
        fields = ["learning_outcome", "weight"]


class AssessmentDetailSerializer(serializers.ModelSerializer):
    learning_outcomes = AssessmentLearningOutcomeDetailSerializer(
        many=True, source="assessmentlearningoutcome_set"
    )
    assessment_type = serializers.CharField(source="name")

    class Meta:
        model = Assesment
        fields = ["assessment_type", "learning_outcomes"]


class CourseDetailSerializer(serializers.ModelSerializer):
    created_by = UserDetailSerializer()
    learning_outcomes = LearningOutcomeDetailSerializer(many=True)
    assessments = AssessmentDetailSerializer(many=True, source="assesments")

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "name",
            "created_by",
            "learning_outcomes",
            "assessments",
        ]
