from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from profiles.models import SavedSearch, SearchNotification
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check saved searches for new candidate matches and send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually sending notifications',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('Running in DRY RUN mode - no notifications will be sent'))
        
        # Get all saved searches with notifications enabled
        saved_searches = SavedSearch.objects.filter(notification_enabled=True)
        
        self.stdout.write(f'Found {saved_searches.count()} saved search(es) with notifications enabled')
        
        total_notifications = 0
        
        for search in saved_searches:
            self.stdout.write(f'\nProcessing: {search.name} (Recruiter: {search.recruiter.user_profile.user.email})')
            
            # Get new candidates for this search
            new_candidates = search.get_new_candidates_since_last_notification()
            
            if new_candidates:
                self.stdout.write(f'  Found {new_candidates.count()} new candidate(s)')
                
                for profile in new_candidates:
                    candidate = profile.user
                    
                    if dry_run:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'  [DRY RUN] Would notify about: {candidate.get_full_name() or candidate.username}'
                            )
                        )
                    else:
                        # Create notification record
                        notification, created = SearchNotification.objects.get_or_create(
                            saved_search=search,
                            candidate=candidate
                        )
                        
                        if created:
                            total_notifications += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Notification created for: {candidate.get_full_name() or candidate.username}'
                                )
                            )
                            
                            # Send email notification
                            self._send_email_notification(search, candidate, profile)
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f'  - Already notified about: {candidate.get_full_name() or candidate.username}'
                                )
                            )
                
                if not dry_run:
                    # Update last_notified timestamp
                    search.last_notified = timezone.now()
                    search.save()
                    self.stdout.write(f'  Updated last_notified timestamp for "{search.name}"')
            else:
                self.stdout.write('  No new candidates found')
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n[DRY RUN COMPLETE] Would have sent {total_notifications} notification(s)'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSent {total_notifications} notification(s) successfully'
                )
            )

    def _send_email_notification(self, search, candidate, profile):
        """Send email notification to recruiter about new candidate match"""
        try:
            recruiter_email = search.recruiter.user_profile.user.email
            recruiter_name = search.recruiter.user_profile.user.get_full_name() or search.recruiter.user_profile.user.username
            candidate_name = candidate.get_full_name() or candidate.username
            
            subject = f'New Candidate Match: {search.name}'
            
            # Build message body
            message_parts = [
                f'Hello {recruiter_name},',
                '',
                f'A new candidate matches your saved search "{search.name}":',
                '',
                f'Candidate: {candidate_name}',
            ]
            
            # Add visible profile information
            visible_fields = profile.get_visible_fields()
            if 'headline' in visible_fields:
                message_parts.append(f'Headline: {visible_fields["headline"]}')
            if 'location' in visible_fields:
                message_parts.append(f'Location: {visible_fields["location"]}')
            if 'skills' in visible_fields:
                skills_preview = visible_fields['skills'][:200]
                message_parts.append(f'Skills: {skills_preview}{"..." if len(visible_fields["skills"]) > 200 else ""}')
            
            message_parts.extend([
                '',
                'View the full profile to learn more.',
                '',
                'To manage your saved searches and notifications, visit your dashboard.',
                '',
                'Best regards,',
                'Job Finder Team'
            ])
            
            message = '\n'.join(message_parts)
            
            # Note: In production, you would send actual emails
            # For now, we'll just log them
            logger.info(f'Email notification would be sent to {recruiter_email}')
            self.stdout.write(f'    Email notification logged for {recruiter_email}')
            
            # Uncomment to actually send emails (requires email configuration in settings.py):
            # send_mail(
            #     subject,
            #     message,
            #     settings.DEFAULT_FROM_EMAIL,
            #     [recruiter_email],
            #     fail_silently=False,
            # )
            
        except Exception as e:
            logger.error(f'Error sending notification email: {e}')
            self.stdout.write(
                self.style.ERROR(f'    Failed to send email: {e}')
            )
