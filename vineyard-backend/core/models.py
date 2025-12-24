from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("student", "Student"),
        ("teacher", "Teacher"),
        ("head", "Department Head"),
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    courses = models.ManyToManyField(
        "Course",
        related_name="students",
        blank=True,
        limit_choices_to={"role": "student"},
    )


class Course(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="courses_created",
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProgramOutcome(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.code} - {self.description}"


class LearningOutcome(models.Model):
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    program_outcomes = models.ManyToManyField(
        ProgramOutcome,
        through="ProgramLearningOutcome",
        related_name="learning_outcomes",
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="learning_outcomes", null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="learning_outcomes_created",
    )

    def __str__(self):
        return f"{self.code} - {self.description}"


class ProgramLearningOutcome(models.Model):
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE)
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE)
    weight = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=1,
        help_text="Weight from 1 (lowest) to 5 (highest)",
    )


class Assesment(models.Model):
    ASSESMENT_TYPES = [
        ("midterm", "Midterm"),
        ("project", "Project"),
        ("final", "Final"),
    ]
    name = models.CharField(max_length=20, choices=ASSESMENT_TYPES, default="midterm")
    learning_outcomes = models.ManyToManyField(
        LearningOutcome, through="AssessmentLearningOutcome", related_name="assessments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assesments", null=True
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assesments_created",
    )

    def __str__(self):
        outcomes = ", ".join(
            f"{alo.learning_outcome.code} (Weight: {alo.weight})"
            for alo in self.assessmentlearningoutcome_set.all()
        )
        return f"{self.get_name_display()} - {outcomes if outcomes else 'No Learning Outcomes'}"


class AssessmentLearningOutcome(models.Model):
    assesment = models.ForeignKey(Assesment, on_delete=models.CASCADE)
    learning_outcome = models.ForeignKey(LearningOutcome, on_delete=models.CASCADE)
    weight = models.IntegerField(
        choices=[(i, str(i)) for i in range(1, 6)],
        default=1,
        help_text="Weight from 1 (lowest) to 5 (highest)",
    )
