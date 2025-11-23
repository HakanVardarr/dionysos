from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    Assesment,
    AssessmentLearningOutcome,
    Course,
    LearningOutcome,
    ProgramLearningOutcome,
    ProgramOutcome,
    User,
)


# ----------------- USER -----------------
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + ((None, {"fields": ("role",)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + ((None, {"fields": ("role",)}),)


# ----------------- COURSE -----------------
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "created_by")
    search_fields = ("code", "name")


# ----------------- PROGRAM OUTCOME -----------------
@admin.register(ProgramOutcome)
class ProgramOutcomeAdmin(admin.ModelAdmin):
    list_display = ("code", "description")
    search_fields = ("code", "description")


# ----------------- LEARNING OUTCOME -----------------
class ProgramLearningOutcomeInline(admin.TabularInline):
    model = ProgramLearningOutcome
    extra = 1


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "description",
        "course",
        "created_by",
        "get_program_outcomes",
    )
    search_fields = ("code", "description")
    list_filter = ("course",)

    inlines = [ProgramLearningOutcomeInline]

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_program_outcomes(self, obj):
        return ", ".join(
            f"{plo.program_outcome.code} (Weight: {plo.weight})"
            for plo in obj.programlearningoutcome_set.all()
        )

    get_program_outcomes.short_description = "Program Outcomes"


# ----------------- ASSESSMENT -----------------
class AssessmentLearningOutcomeInline(admin.TabularInline):
    model = AssessmentLearningOutcome
    extra = 1


@admin.register(Assesment)
class AssesmentAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "get_learning_outcomes")
    inlines = [AssessmentLearningOutcomeInline]
    search_fields = ("name",)
    list_filter = ("course",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def get_learning_outcomes(self, obj):
        return ", ".join(
            f"{alo.learning_outcome.code} (Weight: {alo.weight})"
            for alo in obj.assessmentlearningoutcome_set.all()
        )

    get_learning_outcomes.short_description = "Learning Outcomes"
