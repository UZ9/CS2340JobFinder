from django.db import models
from django.contrib.auth.models import User
from authentication.models import RecruiterProfile


class Job(models.Model):
    WORK_TYPE_CHOICES = [
        ('remote', 'Remote'),
        ('on_site', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True, null=True)  # Optional for remote jobs
    skills_required = models.TextField(help_text="Comma-separated skills")
    salary_min = models.PositiveIntegerField(blank=True, null=True)
    salary_max = models.PositiveIntegerField(blank=True, null=True)
    work_type = models.CharField(max_length=20, choices=WORK_TYPE_CHOICES, default='on_site')
    visa_sponsorship = models.BooleanField(default=False)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='entry')
    recruiter = models.ForeignKey(RecruiterProfile, on_delete=models.CASCADE, related_name='jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company}"

    def get_skills_list(self):
        """Return skills as a list"""
        if self.skills_required:
            return [skill.strip() for skill in self.skills_required.split(',')]
        return []

    def get_salary_range(self):
        """Return formatted salary range"""
        if self.salary_min and self.salary_max:
            return f"${self.salary_min:,} - ${self.salary_max:,}"
        elif self.salary_min:
            return f"${self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to ${self.salary_max:,}"
        return "Salary not specified"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('review', 'Under Review'),
        ('interview', 'Interview'),
        ('offer', 'Offer Extended'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    cover_note = models.TextField(blank=True, null=True, help_text="Personalized note for the application")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    notified_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied', help_text="Last status notified to applicant")
    rejection_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection")
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    notified = models.BooleanField(default=True, help_text="Whether applicant has been notified of current status")

    class Meta:
        unique_together = ('job', 'applicant')  # Prevent duplicate applications
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"
    
    def get_display_status(self):
        """Return the status that should be displayed to applicant (last notified status)"""
        return self.notified_status
    
    def get_display_status_display(self):
        """Return the display name for the notified status"""
        for code, display in self.STATUS_CHOICES:
            if code == self.notified_status:
                return display
        return 'Applied'
    
    def get_status_badge_class(self):
        """Return Bootstrap badge class based on notified status for applicants"""
        status_classes = {
            'applied': 'bg-info',
            'review': 'bg-primary',
            'interview': 'bg-warning',
            'offer': 'bg-success',
            'closed': 'bg-secondary',
            'rejected': 'bg-danger',
        }
        return status_classes.get(self.notified_status, 'bg-secondary')


class Message(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} on {self.application}"
