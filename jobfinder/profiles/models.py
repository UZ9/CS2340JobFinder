from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from authentication.models import RecruiterProfile

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    headline = models.CharField(max_length=200, blank=True, help_text="Your professional headline (e.g., 'Software Engineer with 3 years experience')")
    skills = models.TextField(blank=True, help_text="List your skills separated by commas or new lines")
    education = models.TextField(blank=True, help_text="Your educational background")
    work_experience = models.TextField(blank=True, help_text="Your work experience and achievements")
    links = models.TextField(blank=True, help_text="Professional links (LinkedIn, GitHub, Portfolio, etc.)")
    location = models.CharField(max_length=200, blank=True, help_text="Your current location (e.g., 'New York, NY' or 'San Francisco, CA')")
    projects = models.TextField(blank=True, help_text="Your projects with descriptions, technologies used, etc.")

    # Privacy settings - what recruiters can see
    show_headline = models.BooleanField(default=True, help_text="Show headline to recruiters")
    show_skills = models.BooleanField(default=True, help_text="Show skills to recruiters")
    show_education = models.BooleanField(default=True, help_text="Show education to recruiters")
    show_work_experience = models.BooleanField(default=True, help_text="Show work experience to recruiters")
    show_links = models.BooleanField(default=True, help_text="Show professional links to recruiters")
    show_location = models.BooleanField(default=True, help_text="Show location to recruiters")
    show_projects = models.BooleanField(default=True, help_text="Show projects to recruiters")

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
        if self.show_location and self.location:
            visible_data['location'] = self.location
        if self.show_projects and self.projects:
            visible_data['projects'] = self.projects
        return visible_data


class SavedSearch(models.Model):
    """Model for recruiters to save their candidate searches"""
    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(
        max_length=200,
        help_text='Name for this saved search'
    )
    search_query = models.CharField(
        max_length=500,
        blank=True,
        help_text='General search query'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text='Location filter'
    )
    skills = models.CharField(
        max_length=500,
        blank=True,
        help_text='Skills filter (comma-separated)'
    )
    projects = models.CharField(
        max_length=500,
        blank=True,
        help_text='Projects filter'
    )
    notification_enabled = models.BooleanField(
        default=True,
        help_text='Get notified when new candidates match this search'
    )
    last_notified = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Last time notifications were sent for this search'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Saved searches'

    def __str__(self):
        return f"{self.name} - {self.recruiter.user_profile.user.username}"

    def execute_search(self):
        """Execute the saved search and return matching candidates"""
        from django.db.models import Q
        
        # Start with all profiles where the user is a job seeker
        candidates = Profile.objects.filter(
            user__userprofile__user_type='job_seeker'
        )
        
        # Apply search filters
        if self.search_query:
            # Search across multiple fields
            query = Q()
            search_terms = self.search_query.lower().split()
            for term in search_terms:
                query |= Q(headline__icontains=term)
                query |= Q(skills__icontains=term)
                query |= Q(education__icontains=term)
                query |= Q(work_experience__icontains=term)
                query |= Q(projects__icontains=term)
            candidates = candidates.filter(query)
        
        if self.location:
            candidates = candidates.filter(
                location__icontains=self.location,
                show_location=True
            )
        
        if self.skills:
            # Match any of the skills in the comma-separated list
            skill_list = [s.strip() for s in self.skills.split(',') if s.strip()]
            skill_query = Q()
            for skill in skill_list:
                skill_query |= Q(skills__icontains=skill)
            candidates = candidates.filter(skill_query, show_skills=True)
        
        if self.projects:
            candidates = candidates.filter(
                projects__icontains=self.projects,
                show_projects=True
            )
        
        return candidates.distinct()

    def get_new_candidates_since_last_notification(self):
        """Get candidates that match this search and were updated since last notification"""
        candidates = self.execute_search()
        
        if self.last_notified:
            # Filter for candidates updated after last notification
            candidates = candidates.filter(updated_at__gt=self.last_notified)
        
        # Exclude candidates we've already notified about
        already_notified_ids = self.notifications.values_list('candidate_id', flat=True)
        candidates = candidates.exclude(user_id__in=already_notified_ids)
        
        return candidates


class SearchNotification(models.Model):
    """Track which candidates have been notified for which saved searches"""
    saved_search = models.ForeignKey(
        SavedSearch,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='search_notifications'
    )
    notified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-notified_at']
        unique_together = ('saved_search', 'candidate')

    def __str__(self):
        return f"Notification: {self.saved_search.name} - {self.candidate.username}"

