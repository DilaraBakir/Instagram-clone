from django.apps import AppConfig
# to customize various aspects of the app's behavior


# to automatically add the id as pk and increment it with unique integer field
class CommentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'comment'
