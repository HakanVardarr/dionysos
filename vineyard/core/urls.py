from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard", views.dashboard, name="dashboard"),
    path("dashboard/add_teacher", views.add_teacher, name="add_teacher"),
    path("dashboard/add_student", views.add_student, name="add_student"),
    path("dashboard/program_outcomes", views.program_outcomes, name="program_outcomes"),
    path("dashboard/courses", views.list_courses, name="list_courses"),
    path("dashboard/create_course", views.create_course, name="create_course"),
]
