# Generated by Django 5.1.2 on 2024-11-15 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_businesssettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='businesssettings',
            name='theme_color',
            field=models.CharField(default='#4F46E5', max_length=7, verbose_name='Color principal'),
        ),
    ]