from django.utils import timezone
from datetime import timedelta
from .models import CustomUser

class ActiveUserMiddleware:
    """Update user's online status and last seen time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            now = timezone.now()
            CustomUser.objects.filter(id=request.user.id).update(
                last_seen=now,
                is_online=True
            )
        return response
