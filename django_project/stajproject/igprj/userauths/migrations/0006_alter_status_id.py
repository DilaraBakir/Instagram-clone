# Generated by Django 4.2.3 on 2023-08-09 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userauths', '0005_status_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
