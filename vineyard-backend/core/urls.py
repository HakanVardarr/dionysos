from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard/teachers", views.teachers, name="teachers"),
    path("dashboard/students", views.students, name="students"),
    path("dashboard/program_outcomes", views.program_outcomes, name="program_outcomes"),
    path("dashboard/courses", views.list_courses, name="list_courses"),
    path("dashboard/create_course", views.create_course, name="create_course"),
]
