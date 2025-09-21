from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ("email", "password1", "password2", "user_type")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the username field since we'll use email as username
        if 'username' in self.fields:
            del self.fields['username']

        # Add CSS classes for better styling
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            # Create user profile
            UserProfile.objects.create(
                user=user,
                user_type=self.cleaned_data["user_type"]
            )
        return user


class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )