from core.models import User
from django.contrib.auth.hashers import make_password
from django.core.validators import validate_email
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]


class TeacherCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=25)
    email = serializers.EmailField()

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email already taken")
        return value

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password("dionysos"),
            role="teacher",
            is_staff=True,
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance


class StudentCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=25)
    email = serializers.EmailField()

    def validate_username(self, value):
        qs = User.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        qs = User.objects.filter(email=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Email already taken")
        return value

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password("dionysos"),
            role="student",
            is_staff=False,
        )

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance


class HeadUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=25)
    email = serializers.EmailField(validators=[validate_email])
    password = serializers.CharField(min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            role="head",
            is_superuser=True,
            is_staff=True,
        )
        return user
