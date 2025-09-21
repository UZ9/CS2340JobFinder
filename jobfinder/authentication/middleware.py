from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


class CacheControlMiddleware(MiddlewareMixin):
    """
    Middleware to add cache control headers to prevent back button access after logout
    """
    def process_response(self, request, response):
        # Add cache control headers to authenticated pages
        if hasattr(request, 'user') and request.user.is_authenticated:
            if request.path.startswith('/dashboard') or 'dashboard' in request.path:
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'

        return response


class LogoutRedirectMiddleware(MiddlewareMixin):
    """
    Middleware to handle browser back button after logout
    """
    def process_request(self, request):
        # Check if user is trying to access protected pages after logout
        protected_paths = ['/dashboard/', '/auth/profile/']

        if any(request.path.startswith(path) for path in protected_paths):
            if not request.user.is_authenticated:
                return redirect('home:index')

        return None