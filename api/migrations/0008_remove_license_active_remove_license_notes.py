# Generated by Django 5.1.2 on 2024-11-10 04:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_license_plan'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='license',
            name='active',
        ),
        migrations.RemoveField(
            model_name='license',
            name='notes',
        ),
    ]