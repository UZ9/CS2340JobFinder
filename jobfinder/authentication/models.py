from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    USER_TYPE_CHOICES = [
        ('recruiter', 'Recruiter'),
        ('job_seeker', 'Job Seeker'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"


class RecruiterProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, blank=True, null=True)
    company_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Recruiter: {self.user_profile.user.username}"


class JobSeekerProfile(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    skills = models.TextField(blank=True, null=True, help_text="Comma-separated skills")
    experience_years = models.PositiveIntegerField(default=0)
    resume_uploaded = models.BooleanField(default=False)

    def __str__(self):
        return f"Job Seeker: {self.user_profile.user.username}"
