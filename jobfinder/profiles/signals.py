from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Profile, SavedSearch, SearchNotification


@receiver(post_save, sender=Profile)
def check_saved_searches_on_profile_save(sender, instance, created, **kwargs):
    """
    Automatically check all active saved searches when a profile is created or updated.
    Creates notifications for recruiters whose searches match the profile.
    """
    # Only process if this is a job seeker profile
    try:
        if instance.user.userprofile.user_type != 'job_seeker':
            return
    except:
        return
    
    # Get all saved searches with notifications enabled
    active_searches = SavedSearch.objects.filter(notification_enabled=True)
    
    for search in active_searches:
        # Check if this profile matches the search criteria
        matching_profiles = search.execute_search().filter(id=instance.id)
        
        if matching_profiles.exists():
            # Check if we've already notified about this candidate for this search
            notification_exists = SearchNotification.objects.filter(
                saved_search=search,
                candidate=instance.user
            ).exists()
            
            if not notification_exists:
                # Create notification
                SearchNotification.objects.create(
                    saved_search=search,
                    candidate=instance.user
                )
                
                # Update last_notified timestamp
                search.last_notified = timezone.now()
                search.save()
                
                print(f"✓ Created notification: {search.name} matched {instance.user.username}")
