from core.models import Course, ProgramOutcome, User
from core.serializers import (CourseCreateSerializer, CourseDetailSerializer,
                              CourseSummarySerializer, HeadUserSerializer,
                              ProgramOutcomeCreateSerializer,
                              ProgramOutcomeSerializer,
                              StudentCreateSerializer, TeacherCreateSerializer,
                              UserSerializer)
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
@permission_classes([IsAuthenticated])
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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def courses(request):
    user = request.user
    if request.method == "GET":
        if user.role == "head":
            courses_qs = Course.objects.all()
        elif user.role == "teacher":
            courses_qs = Course.objects.filter(created_by=user)
        else:
            return Response(
                {"detail": "You do not have permission to view courses."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = CourseSummarySerializer(courses_qs, many=True)
        return Response({"courses": serializer.data})

    elif request.method == "POST":
        serializer = CourseCreateSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Course created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def head_or_teacher_required(user):
    return user.role in ["head", "teacher"]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def course_detail(request, course_id):
    if not head_or_teacher_required(request.user):
        return Response(
            {"detail": "You do not have permission to access this course."},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response(
            {"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = CourseDetailSerializer(course, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def filter_students_by_courses(request, course_id):
    if not head_or_teacher_required(request.user):
        return Response(
            {"detail": "You do not have permission to access this course."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response(
            {"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND
        )

    students = User.objects.filter(role="student")
    data = [
        {
            "id": student.id,
            "username": student.username,
            "email": student.email,
            "selected": course.students.filter(id=student.id).exists(),
        }
        for student in students
    ]

    return Response({"students": data}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def assign_students(request, course_id):
    if not head_or_teacher_required(request.user):
        return Response(
            {"detail": "You do not have permission to assign students."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response(
            {"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND
        )

    student_ids = request.data.get("students", [])
    if not isinstance(student_ids, list):
        return Response(
            {"detail": "student_ids must be a list of IDs."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    students = User.objects.filter(id__in=student_ids, role="student")
    course.students.set(students)

    return Response(
        {"detail": f"{students.count()} students assigned to {course.name}."},
        status=status.HTTP_200_OK,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_course(request, course_id):
    if not head_or_teacher_required(request.user):
        return Response(
            {"detail": "You do not have permission to update this course."},
            status=status.HTTP_403_FORBIDDEN,
        )

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response(
            {"detail": "Course not found"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = CourseCreateSerializer(
        course, data=request.data, partial=True, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"message": "Course updated successfully", "course": serializer.data}
        )
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


import json

from celery.result import AsyncResult
from core.tasks import generate


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_generate_task(request):
    uploaded_file = request.FILES.get("file")
    if not uploaded_file:
        return Response({"error": "No file provided"}, status=400)

    program_outcomes_raw = request.data.get("program_outcomes")
    if not program_outcomes_raw:
        return Response({"error": "No program outcomes provided"}, status=400)

    try:
        program_outcomes_list = json.loads(program_outcomes_raw)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON for program_outcomes"}, status=400)

    program_outcomes_str = "\n".join(
        f"{po['code']}: {po['description']}" for po in program_outcomes_list
    )

    file_bytes = uploaded_file.read()
    filename = uploaded_file.name

    task = generate.delay(file_bytes, filename, program_outcomes_str)

    return Response(
        {
            "task_id": task.id,
        },
        status=202,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_generate_task_result(request, task_id):
    """
    Task durumunu kontrol eder ve tamamlandıysa sonucu döner
    """
    task = AsyncResult(task_id)
    if task.state == "SUCCESS":
        return Response({"status": "SUCCESS", "result": task.result})
    else:
        return Response({"status": task.state})
