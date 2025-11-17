import random
import string

from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render

from .decorators import head_required
from .forms import (
    CourseForm,
    CustomUserCreationForm,
    HeadCreateUserForm,
    ProgramOutcomeForm,
)
from .models import Assesment, Course, LearningOutcome

User = get_user_model()


def dashboard(request):
    return render(request, "core/dashboard.html")


def list_courses(request):
    user = request.user
    if user.role == "student":
        return

    if user.role == "teacher":
        courses = Course.objects.filter(created_by=user)
    else:
        courses = Course.objects.all()
    return render(request, "core/list_courses.html", {"courses": courses})


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .models import (
    Assesment,
    AssessmentLearningOutcome,
    Course,
    LearningOutcome,
    ProgramLearningOutcome,
    ProgramOutcome,
)


def create_course(request):
    program_outcomes = ProgramOutcome.objects.all()

    return render(
        request,
        "core/create_course.html",
        {"program_outcomes": list(program_outcomes)},
    )


@head_required
def add_teacher(request):
    if request.method == "POST":
        form = HeadCreateUserForm(request.POST)
        if form.is_valid():
            user, password = form.save(role="teacher")
            return redirect("dashboard")
    else:
        form = HeadCreateUserForm()
    return render(request, "core/add_user.html", {"form": form})


@head_required
def add_student(request):
    if request.method == "POST":
        form = HeadCreateUserForm(request.POST)
        if form.is_valid():
            user, password = form.save(role="student")
            return redirect("dashboard")
    else:
        form = HeadCreateUserForm()
    return render(request, "core/add_user.html", {"form": form})


@head_required
def program_outcomes(request):
    from .models import ProgramOutcome

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
