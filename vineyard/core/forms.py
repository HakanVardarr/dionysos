from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Assesment, Course, LearningOutcome, ProgramOutcome, User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class HeadCreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email")

    def save(self, commit=True, role=None):
        user = super().save(commit=False)
        if role:
            user.role = role
        password = "dionysos"
        user.set_password(password)
        if commit:
            user.save()
        return user, password


class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ("code", "description")
