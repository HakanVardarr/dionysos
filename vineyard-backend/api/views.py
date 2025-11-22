from core.models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(["GET"])
def check_head_user(request):
    exists = User.objects.filter(role="head").exists()
    return Response({"can_create_head": not exists})


@api_view(["POST"])
def register_head_user(request):
    if User.objects.filter(role="head").exists():
        return Response(
            {"error": "Department Head user already exists."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    data = request.data
    username = data["username"]
    email = data["email"]
    password = data["password"]

    if not username or not password or not email:
        return Response(
            {"error": "Username, email, and password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {"error": "Invalid email address."}, status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(email=email).exists():
        return Response(
            {"error": "Email already taken."}, status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create(
        username=username,
        email=email,
        password=make_password(password),
        role="head",
        is_superuser=True,
        is_staff=True,
    )

    return Response(
        {"message": "Department Head user created successfully."},
        status=status.HTTP_201_CREATED,
    )
