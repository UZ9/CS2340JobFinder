from django import forms
from .models import Job, JobApplication


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'company', 'location', 'skills_required',
            'salary_min', 'salary_max', 'work_type', 'visa_sponsorship',
            'experience_level'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Senior Software Engineer'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the job responsibilities, requirements, and benefits...'
            }),
            'company': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Company Name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State/Country (optional for remote jobs)'
            }),
            'skills_required': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Python, Django, JavaScript, React (comma-separated)'
            }),
            'salary_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum salary (USD)'
            }),
            'salary_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum salary (USD)'
            }),
            'work_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'visa_sponsorship': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'experience_level': forms.Select(attrs={
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')

        if salary_min and salary_max and salary_min > salary_max:
            raise forms.ValidationError("Minimum salary cannot be greater than maximum salary.")

        return cleaned_data


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['cover_note']
        widgets = {
            'cover_note': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write a personalized note explaining why you\'re interested in this position and how you can contribute...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cover_note'].required = False


class JobSearchForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by job title, company, or skills...'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Location'
        })
    )
    work_type = forms.ChoiceField(
        choices=[('', 'Any Work Type')] + Job.WORK_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    experience_level = forms.ChoiceField(
        choices=[('', 'Any Experience Level')] + Job.EXPERIENCE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    salary_min = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Salary'
        })
    )
    salary_max = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Salary'
        })
    )
    visa_sponsorship = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )