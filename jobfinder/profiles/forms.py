from django import forms
from .models import Profile, SavedSearch

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['headline', 'skills', 'education', 'work_experience', 'links', 'location', 'projects']
        widgets = {
            'headline': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "Software Engineer with 3 years experience"',
                'maxlength': '200'
            }),
            'skills': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List your skills separated by commas or new lines\nExample: Python, JavaScript, React, Project Management, Agile'
            }),
            'education': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Include your degree, university, graduation year, and any relevant coursework or achievements'
            }),
            'work_experience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Include job titles, companies, dates, and key achievements\nExample:\nSoftware Engineer at TechCorp (2021-2023)\n- Led development of web application\n- Improved performance by 40%'
            }),
            'links': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Include your professional links (one per line)\nExample:\nhttps://linkedin.com/in/yourname\nhttps://github.com/yourusername\nhttps://yourportfolio.com'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "New York, NY" or "San Francisco, CA"',
                'maxlength': '200'
            }),
            'projects': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe your projects with technologies used and outcomes\nExample:\nE-commerce Platform (React, Node.js, MongoDB)\n- Built full-stack web application with 10k+ users\n- Implemented payment integration with Stripe'
            }),
        }
        labels = {
            'headline': 'Professional Headline *',
            'skills': 'Skills *',
            'education': 'Education History *',
            'work_experience': 'Work Experience *',
            'links': 'Professional Links',
            'location': 'Location',
            'projects': 'Projects'
        }
        help_texts = {
            'headline': 'A brief, compelling description of your professional identity',
            'skills': 'List your technical and soft skills that are relevant to your career',
            'education': 'Your educational background including degrees, certifications, and relevant coursework',
            'work_experience': 'Your professional work history with key achievements and responsibilities',
            'links': 'Links to your professional profiles, portfolios, or projects (optional)',
            'location': 'Your current location to help recruiters find local talent (optional)',
            'projects': 'Showcase your personal or professional projects with descriptions and technologies (optional)'
        }

    def clean_headline(self):
        headline = self.cleaned_data.get('headline')
        if not headline or not headline.strip():
            raise forms.ValidationError("Professional headline is required.")
        return headline.strip()

    def clean_skills(self):
        skills = self.cleaned_data.get('skills')
        if not skills or not skills.strip():
            raise forms.ValidationError("Skills are required.")
        return skills.strip()

    def clean_education(self):
        education = self.cleaned_data.get('education')
        if not education or not education.strip():
            raise forms.ValidationError("Education history is required.")
        return education.strip()

    def clean_work_experience(self):
        work_experience = self.cleaned_data.get('work_experience')
        if not work_experience or not work_experience.strip():
            raise forms.ValidationError("Work experience is required.")
        return work_experience.strip()

    def clean_links(self):
        links = self.cleaned_data.get('links', '')
        if links:
            # Basic URL validation
            link_lines = [line.strip() for line in links.split('\n') if line.strip()]
            for link in link_lines:
                if not (link.startswith('http://') or link.startswith('https://')):
                    raise forms.ValidationError(f"Please include full URLs starting with http:// or https://. Found: {link}")
        return links

class PrivacySettingsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['show_headline', 'show_skills', 'show_education',
                 'show_work_experience', 'show_links', 'show_location', 'show_projects']
        widgets = {
            'show_headline': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_skills': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_education': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_work_experience': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_links': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_location': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'show_projects': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'show_headline': 'Show Professional Headline to Recruiters',
            'show_skills': 'Show Skills to Recruiters',
            'show_education': 'Show Education History to Recruiters',
            'show_work_experience': 'Show Work Experience to Recruiters',
            'show_links': 'Show Professional Links to Recruiters',
            'show_location': 'Show Location to Recruiters',
            'show_projects': 'Show Projects to Recruiters'
        }
        help_texts = {
            'show_headline': 'Allow recruiters to see your professional headline',
            'show_skills': 'Allow recruiters to see your skills list',
            'show_education': 'Allow recruiters to see your educational background',
            'show_work_experience': 'Allow recruiters to see your work experience',
            'show_links': 'Allow recruiters to see your professional links',
            'show_location': 'Allow recruiters to see your location',
                        'show_projects': 'Allow recruiters to see your projects'
        }


class SavedSearchForm(forms.ModelForm):
    """Form for creating and editing saved candidate searches"""
    
    class Meta:
        model = SavedSearch
        fields = ['name', 'search_query', 'location', 'skills', 'projects', 'notification_enabled']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "Senior Python Developers in NYC"',
                'maxlength': '200'
            }),
            'search_query': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter keywords to search across all candidate fields',
                'maxlength': '500'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "New York, NY" or "San Francisco"',
                'maxlength': '200'
            }),
            'skills': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "Python, Django, React" (comma-separated)',
                'maxlength': '500'
            }),
            'projects': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Keywords to search in candidate projects',
                'maxlength': '500'
            }),
            'notification_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'name': 'Search Name *',
            'search_query': 'General Search Keywords',
            'location': 'Location',
            'skills': 'Required Skills',
            'projects': 'Project Keywords',
            'notification_enabled': 'Enable Notifications'
        }
        help_texts = {
            'name': 'Give this search a descriptive name so you can easily identify it later',
            'search_query': 'These keywords will be searched across headline, skills, education, experience, and projects',
            'location': 'Filter candidates by location (leave blank for any location)',
            'skills': 'Comma-separated list of skills to search for (candidates matching ANY of these will be included)',
            'projects': 'Keywords to find in candidate project descriptions',
            'notification_enabled': 'Get notified when new candidates match this search criteria'
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name or not name.strip():
            raise forms.ValidationError("Search name is required.")
        return name.strip()

    def clean(self):
        cleaned_data = super().clean()
        # At least one search criterion should be provided
        search_query = cleaned_data.get('search_query', '').strip()
        location = cleaned_data.get('location', '').strip()
        skills = cleaned_data.get('skills', '').strip()
        projects = cleaned_data.get('projects', '').strip()
        
        if not any([search_query, location, skills, projects]):
            raise forms.ValidationError(
                "Please provide at least one search criterion (keywords, location, skills, or projects)."
            )
        
        return cleaned_data


class CandidateSearchForm(forms.Form):
    """Form for quick candidate search without saving"""
    
    search_query = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search keywords...',
        }),
        label='Search'
    )
    location = forms.CharField(
        required=False,
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location...',
        }),
        label='Location'
    )
    skills = forms.CharField(
        required=False,
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Skills (comma-separated)...',
        }),
        label='Skills'
    )
