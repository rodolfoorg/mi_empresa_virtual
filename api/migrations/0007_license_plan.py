# Generated by Django 5.1.2 on 2024-11-10 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_alter_business_unique_together_alter_business_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='plan',
            field=models.CharField(choices=[('basico', 'Básico'), ('avanzado', 'Avanzado'), ('pro', 'Pro')], default='basico', max_length=10),
        ),
    ]
