# Generated by Django 5.1.2 on 2024-11-23 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_product_purchase_product_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='card',
            name='is_business',
            field=models.BooleanField(default=True, null=True),
        ),
    ]
