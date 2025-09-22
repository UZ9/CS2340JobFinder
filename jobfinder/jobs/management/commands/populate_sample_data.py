from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from authentication.models import UserProfile, RecruiterProfile, JobSeekerProfile
from jobs.models import Job


class Command(BaseCommand):
    help = 'Populate the database with sample jobs and users'

    def handle(self, *args, **options):
        # Create sample recruiter
        recruiter_user = User.objects.create_user(
            username='recruiter1',
            email='recruiter1@example.com',
            password='password123',
            first_name='John',
            last_name='Recruiter'
        )
        recruiter_profile = UserProfile.objects.create(
            user=recruiter_user,
            user_type='recruiter'
        )
        recruiter = RecruiterProfile.objects.create(
            user_profile=recruiter_profile,
            company_name='TechCorp Inc.',
            company_description='Leading technology company focused on innovation'
        )

        # Create sample job seeker
        jobseeker_user = User.objects.create_user(
            username='jobseeker1',
            email='jobseeker1@example.com',
            password='password123',
            first_name='Jane',
            last_name='Seeker'
        )
        jobseeker_profile = UserProfile.objects.create(
            user=jobseeker_user,
            user_type='job_seeker'
        )
        jobseeker = JobSeekerProfile.objects.create(
            user_profile=jobseeker_profile,
            skills='Python, Django, JavaScript, React',
            experience_years=3
        )

        # Sample jobs data
        sample_jobs = [
            {
                'title': 'Senior Software Engineer',
                'description': 'We are looking for a Senior Software Engineer to join our dynamic team. You will be responsible for designing, developing, and maintaining high-quality software applications. The ideal candidate has strong experience with Python, Django, and modern web technologies.',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'skills_required': 'Python, Django, PostgreSQL, JavaScript, React',
                'salary_min': 120000,
                'salary_max': 160000,
                'work_type': 'hybrid',
                'visa_sponsorship': True,
                'experience_level': 'senior',
            },
            {
                'title': 'Frontend Developer',
                'description': 'Join our frontend team to build amazing user experiences. We need someone who is passionate about creating responsive, accessible, and performant web applications using modern JavaScript frameworks.',
                'company': 'WebDesign Studio',
                'location': 'New York, NY',
                'skills_required': 'JavaScript, React, CSS, HTML, TypeScript',
                'salary_min': 80000,
                'salary_max': 110000,
                'work_type': 'on_site',
                'visa_sponsorship': False,
                'experience_level': 'mid',
            },
            {
                'title': 'Python Backend Developer',
                'description': 'Remote opportunity for a Python developer to work on scalable backend systems. Experience with Django, FastAPI, and cloud technologies preferred. Great opportunity for growth and learning.',
                'company': 'CloudTech Solutions',
                'location': '',
                'skills_required': 'Python, Django, FastAPI, AWS, Docker',
                'salary_min': 90000,
                'salary_max': 130000,
                'work_type': 'remote',
                'visa_sponsorship': True,
                'experience_level': 'mid',
            },
            {
                'title': 'Junior Full Stack Developer',
                'description': 'Perfect entry-level position for new graduates or career changers. You will work with both frontend and backend technologies while learning from experienced developers in a supportive environment.',
                'company': 'StartupXYZ',
                'location': 'Austin, TX',
                'skills_required': 'JavaScript, Python, HTML, CSS, SQL',
                'salary_min': 60000,
                'salary_max': 80000,
                'work_type': 'hybrid',
                'visa_sponsorship': False,
                'experience_level': 'entry',
            },
            {
                'title': 'DevOps Engineer',
                'description': 'We need a DevOps engineer to help us build and maintain our cloud infrastructure. Experience with CI/CD, containerization, and cloud platforms is essential.',
                'company': 'InfraTech Corp',
                'location': 'Seattle, WA',
                'skills_required': 'AWS, Docker, Kubernetes, Jenkins, Python',
                'salary_min': 100000,
                'salary_max': 140000,
                'work_type': 'on_site',
                'visa_sponsorship': True,
                'experience_level': 'senior',
            },
            {
                'title': 'Data Scientist',
                'description': 'Join our data science team to extract insights from large datasets. You will work on machine learning models, data analysis, and creating data-driven solutions for business problems.',
                'company': 'DataAnalytics Pro',
                'location': '',
                'skills_required': 'Python, SQL, Machine Learning, Pandas, Scikit-learn',
                'salary_min': 95000,
                'salary_max': 135000,
                'work_type': 'remote',
                'visa_sponsorship': True,
                'experience_level': 'mid',
            }
        ]

        # Create sample jobs
        for job_data in sample_jobs:
            job = Job.objects.create(
                recruiter=recruiter,
                **job_data
            )
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {len(sample_jobs)} sample jobs, 1 recruiter, and 1 job seeker'
            )
        )