# Generated by Django 5.1.2 on 2024-11-09 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_emailverificationtoken'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='license',
            name='is_pro',
        ),
        migrations.RemoveField(
            model_name='license',
            name='plan',
        ),
    ]