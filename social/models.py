from django.db import models

from django.contrib.auth.models import User


# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to="profile_pics", default="default.jpg"
    )  # Set your default image path here
    followers = models.ManyToManyField(User, related_name="following", blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
