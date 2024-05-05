from django.contrib import admin
from comment.models import Comment


# to add comments from the admin page
admin.site.register(Comment)
