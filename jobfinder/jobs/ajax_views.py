"""
AJAX and API views for job application management
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from authentication.models import UserProfile, RecruiterProfile
from profiles.models import Profile
from .models import Job, JobApplication, Message
import json


@login_required
@require_POST
def update_application_status(request):
    """AJAX endpoint to update a single application status"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        new_status = data.get('status')
        notify = data.get('notify', False)
        
        print(f"DEBUG: update_application_status called - ID: {application_id}, Status: {new_status}, Notify: {notify}")
        
        # Verify recruiter owns this job
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
        application = get_object_or_404(JobApplication, id=application_id)
        
        if application.job.recruiter != recruiter_profile:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        print(f"DEBUG: Before update - status: {application.status}, notified_status: {application.notified_status}, notified: {application.notified}")
        
        # Update status
        application.status = new_status
        application.status_updated_at = timezone.now()
        application.notified = notify
        
        # If notifying, update the notified_status to current status
        if notify:
            application.notified_status = new_status
            print(f"DEBUG: Notifying applicant - setting notified_status to {new_status}")
        
        application.save()
        
        print(f"DEBUG: After save - status: {application.status}, notified_status: {application.notified_status}, notified: {application.notified}")
        
        return JsonResponse({
            'success': True,
            'application_id': application.id,
            'status': application.status,
            'notified': application.notified,
            'notified_status': application.notified_status
        })
    
    except Exception as e:
        print(f"DEBUG: Error in update_application_status: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def batch_update_status(request):
    """AJAX endpoint to batch notify applicants of their current status"""
    try:
        data = json.loads(request.body)
        application_ids = data.get('application_ids', [])
        status = data.get('status')  # Status is just for verification, not updating
        
        # Verify recruiter owns these jobs
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
        
        applications = JobApplication.objects.filter(
            id__in=application_ids,
            job__recruiter=recruiter_profile
        )
        
        # Only update notified flag and notified_status, don't change current status
        updated_count = 0
        for application in applications:
            # Update notified_status to match current status
            application.notified_status = application.status
            application.notified = True
            application.save()
            updated_count += 1
        
        return JsonResponse({
            'success': True,
            'updated_count': updated_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def delete_application(request):
    """AJAX endpoint to delete/reject an application"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        rejection_reason = data.get('rejection_reason', '')
        
        # Verify recruiter owns this job
        user_profile = UserProfile.objects.get(user=request.user)
        if user_profile.user_type != 'recruiter':
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
        application = get_object_or_404(JobApplication, id=application_id)
        
        if application.job.recruiter != recruiter_profile:
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        # Mark as rejected instead of deleting
        application.status = 'rejected'
        application.rejection_reason = rejection_reason
        application.status_updated_at = timezone.now()
        application.notified = True
        application.notified_status = 'rejected'
        application.save()
        
        return JsonResponse({
            'success': True,
            'application_id': application.id
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def application_messages(request, application_id):
    """View messages for a specific application"""
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Check if user is involved in this application
    user_profile = UserProfile.objects.get(user=request.user)
    
    is_recruiter = (user_profile.user_type == 'recruiter' and 
                   application.job.recruiter.user_profile == user_profile)
    is_applicant = application.applicant == request.user
    
    if not (is_recruiter or is_applicant):
        return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
    
    # Mark messages as read for the current user
    Message.objects.filter(
        application=application
    ).exclude(sender=request.user).update(is_read=True)
    
    messages_list = []
    for msg in application.messages.all():
        messages_list.append({
            'id': msg.id,
            'sender': msg.sender.get_full_name() or msg.sender.username,
            'sender_id': msg.sender.id,
            'content': msg.content,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_read': msg.is_read,
            'is_own': msg.sender == request.user
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_list,
        'application': {
            'id': application.id,
            'job_title': application.job.title,
            'applicant': application.applicant.get_full_name() or application.applicant.username,
            'status': application.status
        }
    })


@login_required
@require_POST
def send_message(request):
    """Send a message for an application"""
    try:
        data = json.loads(request.body)
        application_id = data.get('application_id')
        content = data.get('content', '').strip()
        
        if not content:
            return JsonResponse({'success': False, 'error': 'Message cannot be empty'}, status=400)
        
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Check if user is involved in this application
        user_profile = UserProfile.objects.get(user=request.user)
        
        is_recruiter = (user_profile.user_type == 'recruiter' and 
                       application.job.recruiter.user_profile == user_profile)
        is_applicant = application.applicant == request.user
        
        if not (is_recruiter or is_applicant):
            return JsonResponse({'success': False, 'error': 'Not authorized'}, status=403)
        
        # Create message
        message = Message.objects.create(
            application=application,
            sender=request.user,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'sender': message.sender.get_full_name() or message.sender.username,
                'content': message.content,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
                'is_own': True
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_unread_message_count(request):
    """Get count of unread messages for current user"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.user_type == 'recruiter':
            recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
            # Count messages in applications for recruiter's jobs
            unread_count = Message.objects.filter(
                application__job__recruiter=recruiter_profile,
                is_read=False
            ).exclude(sender=request.user).count()
        else:
            # Count messages in user's applications
            unread_count = Message.objects.filter(
                application__applicant=request.user,
                is_read=False
            ).exclude(sender=request.user).count()
        
        return JsonResponse({
            'success': True,
            'unread_count': unread_count
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_conversations(request):
    """Get all conversations for current user"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        conversations = []
        
        if user_profile.user_type == 'recruiter':
            recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
            # Get all applications for recruiter's jobs that have messages
            applications = JobApplication.objects.filter(
                job__recruiter=recruiter_profile
            ).exclude(messages=None).distinct()
            
            for app in applications:
                last_message = app.messages.order_by('-created_at').first()
                unread_count = app.messages.filter(is_read=False).exclude(sender=request.user).count()
                
                conversations.append({
                    'application_id': app.id,
                    'job_title': app.job.title,
                    'other_party': app.applicant.get_full_name() or app.applicant.username,
                    'last_message': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else ''),
                    'last_message_time': last_message.created_at.strftime('%b %d, %H:%M') if last_message else '',
                    'unread_count': unread_count
                })
        else:
            # Get all applications by job seeker that have messages
            applications = JobApplication.objects.filter(
                applicant=request.user
            ).exclude(messages=None).distinct()
            
            for app in applications:
                last_message = app.messages.order_by('-created_at').first()
                unread_count = app.messages.filter(is_read=False).exclude(sender=request.user).count()
                
                conversations.append({
                    'application_id': app.id,
                    'job_title': app.job.title,
                    'other_party': app.job.company,
                    'last_message': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else ''),
                    'last_message_time': last_message.created_at.strftime('%b %d, %H:%M') if last_message else '',
                    'unread_count': unread_count
                })
        
        # Sort by last message time
        conversations.sort(key=lambda x: x['last_message_time'], reverse=True)
        
        # Calculate total unread count
        total_unread = sum(conv['unread_count'] for conv in conversations)
        
        return JsonResponse({
            'success': True,
            'conversations': conversations,
            'unread_count': total_unread
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_applicant_locations(request, job_id):
    """AJAX endpoint to get applicant locations for map clustering"""
    try:
        # Verify recruiter owns this job
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User profile not found'}, status=403)
        
        if user_profile.user_type != 'recruiter':
            return JsonResponse({'success': False, 'error': 'Not authorized - only recruiters can view applicant locations'}, status=403)
        
        try:
            recruiter_profile = RecruiterProfile.objects.get(user_profile=user_profile)
        except RecruiterProfile.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Recruiter profile not found'}, status=403)
        
        try:
            job = Job.objects.get(id=job_id, recruiter=recruiter_profile)
        except Job.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Job not found or you do not have permission to view it'}, status=404)
        
        # Get all applicants for this job
        applications = job.applications.all()
        
        locations = []
        for application in applications:
            try:
                # Get the applicant's profile
                profile = Profile.objects.get(user=application.applicant)
                
                # Only include if location sharing is enabled and coordinates exist
                if profile.show_location and profile.latitude is not None and profile.longitude is not None:
                    locations.append({
                        'lat': float(profile.latitude),
                        'lng': float(profile.longitude),
                        'name': application.applicant.get_full_name() or application.applicant.username,
                        'location': profile.location or 'Location not specified',
                        'status': application.get_status_display(),
                        'status_code': application.status,
                        'applied_at': application.applied_at.strftime('%b %d, %Y'),
                        'application_id': application.id
                    })
            except Profile.DoesNotExist:
                # Skip if profile doesn't exist
                continue
            except (ValueError, TypeError) as e:
                print(f"Invalid coordinates for user {application.applicant.id}: {e}")
                continue
        
        return JsonResponse({
            'success': True,
            'locations': locations,
            'count': len(locations)
        })
    
    except Exception as e:
        import traceback
        print(f"Error in get_applicant_locations: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)

