# Generated by Django 4.2.3 on 2023-07-24 13:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('directs', '0002_remove_message_user'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='message',
        #     name='user',
        #     field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        #     preserve_default=False,
        # ),
    ]