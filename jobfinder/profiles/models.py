from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=200, blank=True, help_text="Your professional headline (e.g., 'Software Engineer with 3 years experience')")
    skills = models.TextField(blank=True, help_text="List your skills separated by commas or new lines")
    education = models.TextField(blank=True, help_text="Your educational background")
    work_experience = models.TextField(blank=True, help_text="Your work experience and achievements")
    links = models.TextField(blank=True, help_text="Professional links (LinkedIn, GitHub, Portfolio, etc.)")

    # Privacy settings - what recruiters can see
    show_headline = models.BooleanField(default=True, help_text="Show headline to recruiters")
    show_skills = models.BooleanField(default=True, help_text="Show skills to recruiters")
    show_education = models.BooleanField(default=True, help_text="Show education to recruiters")
    show_work_experience = models.BooleanField(default=True, help_text="Show work experience to recruiters")
    show_links = models.BooleanField(default=True, help_text="Show professional links to recruiters")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
    def get_visible_fields(self):
        """Return only the fields that are visible to recruiters based on privacy settings"""
        visible_data = {}
        if self.show_headline and self.headline:
            visible_data['headline'] = self.headline
        if self.show_skills and self.skills:
            visible_data['skills'] = self.skills
        if self.show_education and self.education:
            visible_data['education'] = self.education
        if self.show_work_experience and self.work_experience:
            visible_data['work_experience'] = self.work_experience
        if self.show_links and self.links:
            visible_data['links'] = self.links
        return visible_data

