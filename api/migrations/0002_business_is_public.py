# Generated by Django 5.1.2 on 2024-11-08 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='business',
            name='is_public',
            field=models.BooleanField(default=True),
        ),
    ]