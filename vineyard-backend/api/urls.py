from django.urls import path

from . import views

urlpatterns = [
    path("check-head-user/", views.check_head_user, name="check_user"),
    path("register-head-user/", views.register_head_user, name="register_head_user"),
]
