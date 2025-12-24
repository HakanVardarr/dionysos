from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

urlpatterns = [
    path("check-head-user/", views.check_head_user, name="check_user"),
    path("register-head-user/", views.register_head_user, name="register_head_user"),
    path("me/", views.me, name="me"),
    path("teachers/", views.teachers, name="teachers"),
    path("teachers/bulk/", views.bulk_upload_teachers, name="teachers_bulk"),
    path("teachers/<int:id>/", views.teacher_detail, name="teacher_detail"),
    path("students/", views.students, name="students"),
    path("students/bulk/", views.bulk_upload_students, name="students_bulk"),
    path("students/<int:id>/", views.student_detail, name="student_detail"),
    path("program-outcomes/", views.program_outcomes, name="program_outcomes"),
    path("courses/", views.courses, name="courses"),
    path("courses/<int:course_id>/", views.course_detail, name="course_detail"),
    path("courses/<int:course_id>/edit/", views.update_course, name="update_course"),
    path(
        "courses/<int:course_id>/assign-students/",
        views.assign_students,
        name="assign_students",
    ),
    path(
        "courses/<int:course_id>/students/",
        views.filter_students_by_courses,
        name="filter_students_by_courses",
    ),
    path("token/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
