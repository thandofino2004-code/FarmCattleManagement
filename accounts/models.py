from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_approved = models.BooleanField(default=False, help_text="Admin approval required")
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    farm_name = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {'Approved' if self.is_approved else 'Pending'}"
    
    class Meta:
        verbose_name_plural = "User Profiles"

# Auto-create profile when user registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
# Create your models here.
