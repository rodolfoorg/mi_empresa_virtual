# Generated by Django 5.1.2 on 2024-10-28 22:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_license_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='license',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 11, 25, 22, 50, 41, 107250, tzinfo=datetime.timezone.utc)),
        ),
    ]
