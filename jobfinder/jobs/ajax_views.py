"""
AJAX and API views for job application management
"""
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone
from authentication.models import UserProfile, RecruiterProfile
from .models import Job, JobApplication, Message
import json
import math


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


def _haversine_distance_km(lat1, lon1, lat2, lon2):
    """Return distance between two lat/lon points in kilometers."""
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6371.0088 * c
    return km


def get_jobs_geo(request):
    """Return jobs with coordinates as JSON. Optional GET params: lat, lng, max_distance_km."""
    try:
        jobs_qs = Job.objects.filter(is_active=True)

        # Parse optional filters
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        max_distance = request.GET.get('max_distance_km')

        jobs_list = []

        # Convert to floats when provided
        try:
            lat = float(lat) if lat is not None else None
            lng = float(lng) if lng is not None else None
            max_distance = float(max_distance) if max_distance is not None else None
        except (TypeError, ValueError):
            lat = lng = max_distance = None

        for job in jobs_qs:
            if job.latitude is None or job.longitude is None:
                continue

            distance_km = None
            if lat is not None and lng is not None:
                distance_km = _haversine_distance_km(lat, lng, job.latitude, job.longitude)

                if max_distance is not None and distance_km > max_distance:
                    # skip jobs outside radius
                    continue

            jobs_list.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'latitude': job.latitude,
                'longitude': job.longitude,
                'distance_km': round(distance_km, 2) if distance_km is not None else None,
                'detail_url': f"{request.scheme}://{request.get_host()}{request.build_absolute_uri('/').rstrip('/')}/jobs/{job.id}/",
            })

        return JsonResponse({'success': True, 'jobs': jobs_list})

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

