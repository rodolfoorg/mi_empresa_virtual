# Generated by Django 5.1.2 on 2024-11-22 22:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='Product',
            new_name='product',
        ),
        migrations.RenameField(
            model_name='sale',
            old_name='Product',
            new_name='product',
        ),
    ]