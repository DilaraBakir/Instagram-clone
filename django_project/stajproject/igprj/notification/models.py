from django.db import models
from django.contrib.auth.models import User
from post.models import Post, Likes, Follow
from comment.models import Comment


class Notification(models.Model):
    LIKE = 'like'
    COMMENT = 'comment'
    FOLLOW = 'follow'
    NOTIFICATION_TYPES = [
        (LIKE, 'Like'),
        (COMMENT, 'Comment'),
        (FOLLOW, 'Follow'),
    ]

    action = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_notifications')
    post = models.ForeignKey(Post, on_delete=models.SET_NULL, blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=True)
    like = models.ForeignKey(Likes, on_delete=models.SET_NULL, blank=True, null=True)
    follow = models.ForeignKey(Follow, on_delete=models.SET_NULL, blank=True, null=True)
