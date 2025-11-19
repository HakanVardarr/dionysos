import json

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.shortcuts import redirect, render

from .decorators import head_required, staff_required
from .forms import CustomUserCreationForm, HeadCreateUserForm, ProgramOutcomeForm
from .models import (
    Assesment,
    AssessmentLearningOutcome,
    Course,
    LearningOutcome,
    ProgramLearningOutcome,
    ProgramOutcome,
)

User = get_user_model()


def dashboard(request):
    return render(request, "core/dashboard.html")


@staff_required
def list_courses(request):
    user = request.user
    if user.role == "teacher":
        courses = Course.objects.filter(created_by=user)
    else:
        courses = Course.objects.all()
    return render(request, "core/list_courses.html", {"courses": courses})


@staff_required
def create_course(request):
    user = request.user if request.user.is_authenticated else None

    if request.method == "POST":
        data = json.loads(request.body)
        try:
            with transaction.atomic():
                course_code = data.get("course_code")
                course_name = data.get("course_name")

                course = Course.objects.create(
                    code=course_code, name=course_name, created_by=user
                )

                lo_instances = {}
                for lo in data.get("learning_outcomes", []):
                    lo_instance = LearningOutcome.objects.create(
                        code=lo["code"],
                        description=lo["description"],
                        course=course,
                        created_by=user,
                    )
                    lo_instances[lo["code"]] = lo_instance

                    for po in lo.get("program_outcomes", []):
                        po_instance = ProgramOutcome.objects.get(code=po["code"])
                        ProgramLearningOutcome.objects.create(
                            learning_outcome=lo_instance,
                            program_outcome=po_instance,
                            weight=int(po["weight"]),
                        )

                for assessment in data.get("assessments", []):
                    ass_instance = Assesment.objects.create(
                        name=assessment["assessment_type"],
                        course=course,
                        created_by=user,
                    )

                    for alo in assessment.get("learning_outcomes", []):
                        lo_instance = lo_instances.get(alo["code"])
                        if lo_instance:
                            AssessmentLearningOutcome.objects.create(
                                assesment=ass_instance,
                                learning_outcome=lo_instance,
                                weight=int(alo["weight"]),
                            )

            return JsonResponse(
                {"status": "success", "message": "Course and related data created."}
            )
        except IntegrityError as e:
            return JsonResponse(
                {"status": "error", "message": f"Database error: {str(e)}"}, status=400
            )
        except ProgramOutcome.DoesNotExist as e:
            return JsonResponse(
                {"status": "error", "message": f"ProgramOutcome not found: {str(e)}"},
                status=400,
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": f"Unexpected error: {str(e)}"},
                status=500,
            )

    program_outcomes = ProgramOutcome.objects.all()

    return render(
        request,
        "core/create_course.html",
        {"program_outcomes": list(program_outcomes)},
    )


@head_required
def teachers(request):
    if request.method == "POST":
        form = HeadCreateUserForm(request.POST)
        if form.is_valid():
            user, password = form.save(role="teacher")
            return redirect("teachers")
    else:
        form = HeadCreateUserForm()
    teachers = list(User.objects.filter(role="teacher"))
    return render(request, "core/teachers.html", {"form": form, "teachers": teachers})


@head_required
def students(request):
    if request.method == "POST":
        form = HeadCreateUserForm(request.POST)
        if form.is_valid():
            user, password = form.save(role="student")
            return redirect("students")
    else:
        form = HeadCreateUserForm()

    query = request.GET.get("q", "")
    if query:
        try:
            student = User.objects.get(role="student", username=query)
        except User.DoesNotExist:
            student = None

        return render(request, "core/student_detail.html", {"student": student})

    # Query yoksa tüm öğrenciler
    students = User.objects.filter(role="student")
    return render(request, "core/students.html", {"form": form, "students": students})


@head_required
def program_outcomes(request):

    if request.method == "POST":
        form = ProgramOutcomeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("program_outcomes")
    else:
        form = ProgramOutcomeForm()
    outcomes = ProgramOutcome.objects.all()
    return render(
        request, "core/program_outcomes.html", {"form": form, "outcomes": outcomes}
    )


def home(request):
    if not User.objects.filter(role="head").exists():
        if request.method == "POST":
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.role = "head"
                user.is_superuser = True
                user.is_staff = True
                user.save()
                return redirect("home")
        else:
            form = CustomUserCreationForm()
        return render(request, "core/create_head.html", {"form": form})

    return render(request, "core/home.html")
