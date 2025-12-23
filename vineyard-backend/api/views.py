from core.models import Course, ProgramOutcome, User
from core.serializers import (
    HeadUserSerializer,
    ProgramOutcomeCreateSerializer,
    ProgramOutcomeSerializer,
    StudentCreateSerializer,
    TeacherCreateSerializer,
    UserSerializer,
)
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
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
    serializer = HeadUserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Department Head user created successfully."},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    return Response(
        {
            "username": user.username,
            "role": user.role,
        }
    )


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def teachers(request):
    if request.method == "GET":
        teachers = User.objects.filter(role="teacher")
        serializer = UserSerializer(teachers, many=True)
        return Response({"teachers": serializer.data})

    elif request.method == "POST":
        serializer = TeacherCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Teacher created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def teacher_detail(request, id):
    try:
        teacher = User.objects.get(id=id, role="teacher")
    except User.DoesNotExist:
        return Response(
            {"detail": "Teacher not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "PUT":
        serializer = TeacherCreateSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Teacher updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        teacher.delete()
        return Response({"message": "Teacher deleted successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_upload_teachers(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"detail": "No file provided"}, status=400)

    import csv
    import io

    decoded_file = io.TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(decoded_file)
    created = 0

    for row in reader:
        try:
            _ = User.objects.create_user(
                username=row["username"],
                email=row["email"],
                role="teacher",
                password="dionysos",
            )
            created += 1
        except Exception as e:
            continue

    return Response({"message": f"{created} teachers created successfully."})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def students(request):
    if request.method == "GET":
        students = User.objects.filter(role="student")
        serializer = UserSerializer(students, many=True)
        return Response({"students": serializer.data})

    elif request.method == "POST":
        serializer = StudentCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Student created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def student_detail(request, id):
    try:
        student = User.objects.get(id=id, role="student")
    except User.DoesNotExist:
        return Response(
            {"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND
        )

    if request.method == "PUT":
        serializer = StudentCreateSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Student updated successfully."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        student.delete()
        return Response({"message": "Student deleted successfully."})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def bulk_upload_students(request):
    file = request.FILES.get("file")
    if not file:
        return Response({"detail": "No file provided"}, status=400)

    import csv
    import io

    decoded_file = io.TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(decoded_file)
    created = 0

    for row in reader:
        try:
            _ = User.objects.create_user(
                username=row["username"],
                email=row["email"],
                role="student",
                password="dionysos",
            )
            created += 1
        except Exception as e:
            continue

    return Response({"message": f"{created} students created successfully."})


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def program_outcomes(request):
    if request.method == "GET":
        program_outcomes = ProgramOutcome.objects.all()
        serializer = ProgramOutcomeSerializer(program_outcomes, many=True)
        return Response({"program-outcomes": serializer.data})
    elif request.method == "POST":
        serializer = ProgramOutcomeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Outcome created successfully."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
