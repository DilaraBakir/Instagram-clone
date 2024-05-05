import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.db.models.signals import post_save, post_delete
from django.urls import reverse
from django.utils.text import slugify


# Uploading user files to a specific directory (photos etc.)
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


class Tag(models.Model):
    title = models.CharField(max_length=100, verbose_name="Tag")
    # url friendly version of a string to search tags - not added yet :(
    #  to generate unique identifiers, a UUID version 1, which is based on the host ID, sequence number, and the current timestamp
    slug = models.SlugField(null=False, unique=True, default=uuid.uuid1)

    class Meta:
        verbose_name = 'Tag'  # human-readable name
        verbose_name_plural = 'Tags'

  # def get_absolute_url(self):
  #     return reverse('tags', args=[self.slug])

    # to get the title of the tag when the tag is printed
    def __str__(self):
        return self.title

    # to save the tag
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.slug)
        return super().save(*args, **kwargs)


class Post(models.Model):
    # uuid4 is random
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    picture = models.ImageField(upload_to=user_directory_path, verbose_name="Picture", null=False)
    caption = models.CharField(max_length=10000000, verbose_name="Caption")
    posted = models.DateTimeField(auto_now_add=True)
    # for a post to have multiple tags
    tag = models.ManyToManyField(Tag, related_name="tags")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)

    # to connect the post by post id to an url to see the post in detail
    def get_absolute_url(self):
        return reverse('post-detail', args=[str(self.id)])

    # def __str__(self):
    #   return self.caption


class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")


class Likes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")
    is_liked = models.BooleanField(default=False)


class Stream(models.Model):
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stream_following")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stream_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    date = models.DateTimeField()

    def add_post(sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream = Stream(post=post, user=follower.follower, date=post.posted, following=user)
            stream.save()

# signal receiver, when a post is saved add_post will be called
post_save.connect(Stream.add_post, sender=Post)


