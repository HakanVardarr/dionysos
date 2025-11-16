from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string

from .models import ProgramOutcome, User


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
        password = get_random_string(length=8)
        user.set_password(password)
        if commit:
            user.save()
        return user, password


class ProgramOutcomeForm(forms.ModelForm):
    class Meta:
        model = ProgramOutcome
        fields = ("code", "description")
