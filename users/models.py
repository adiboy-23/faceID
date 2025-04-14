from django.db import models
from django.contrib.auth.models import User
import os

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    passport_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField()
    hotel_name = models.CharField(max_length=100)
    room_number = models.CharField(max_length=10)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    face_image = models.ImageField(upload_to='face_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def save(self, *args, **kwargs):
        # Ensure the face_images directory exists
        if self.face_image:
            upload_path = self.face_image.field.upload_to
            if upload_path:
                from django.conf import settings
                full_path = os.path.join(settings.MEDIA_ROOT, upload_path)
                os.makedirs(full_path, exist_ok=True)
        super().save(*args, **kwargs)
