from django.db import models
from django.contrib.auth.models import User
from post.models import Post
from PIL import Image
from django.db.models.signals import post_save
from django.utils import timezone


# uploading user files to a specific directory
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    location = models.CharField(max_length=50, null=True, blank=True)
    url = models.URLField(max_length=1000, null=True, blank=True)
    bio = models.TextField(max_length=150, null=True, blank=True)
    created = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True, verbose_name='Picture', default="default.png")
    favourite = models.ManyToManyField(Post)

    def __str__(self):
        if self.first_name is None:
            return 'None'
        return f'{self.user.username} - Profile'

    def save(self, *args, **kwargs):
        super().save(*args, ** kwargs)
        SIZE = 300, 300

        if self.image:
            image = Image.open(self.image.path)
            image.thumbnail(SIZE, Image.LANCZOS)
            image.save(self.image.path)

    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    # connect method to link a signal handler function to a signal
    post_save.connect(create_user_profile, sender=User)
    post_save.connect(save_user_profile, sender=User)


class Status(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status')
    file = models.ImageField(upload_to='status')
    created_at = models.DateTimeField(auto_now_add=True)
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"Status {self.id} by {self.user.username}"

