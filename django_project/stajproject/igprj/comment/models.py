from django.db import models
from django.contrib.auth.models import User
from post.models import Post


class Comment(models.Model):
    # ForeignKey to establish a relationship between post and comment, each comment belongs to a specific post
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)


