from datetime import timedelta
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    profile_img = models.ImageField(upload_to="profile_images", default="blank.webp")
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField()
    last_seen = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    
    
    def last_seen_display(self):
        """Return human-readable last seen status."""
        if self.is_online:
            return "Active now"
        if self.last_seen:
            diff = timezone.now() - self.last_seen
            if diff < timedelta(minutes=1):
                return "Just now"
            elif diff < timedelta(hours=1):
                mins = diff.seconds // 60
                return f"{mins} minute{'s' if mins > 1 else ''} ago"
            elif diff < timedelta(days=1):
                return self.last_seen.strftime("Today at %I:%M %p")
            else:
                return self.last_seen.strftime("%b %d at %I:%M %p")
        return "Offline"

class Message(models.Model):
    sender = models.ForeignKey(CustomUser, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    edited = models.BooleanField(default=False) 


    def __str__(self):
        return f"{self.sender.username} → {self.receiver.username}: {self.content[:25]}"


class Room(models.Model):
    """Optional — use if you want multiple chat rooms"""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name