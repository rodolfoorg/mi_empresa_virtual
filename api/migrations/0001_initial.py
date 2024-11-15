# Generated by Django 5.1.2 on 2024-11-03 07:11

import api.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner', models.CharField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, default='No especificado', max_length=15, null=True)),
                ('province', models.CharField(max_length=100)),
                ('municipality', models.CharField(max_length=100)),
                ('street', models.CharField(blank=True, max_length=200, null=True)),
                ('house_number', models.CharField(blank=True, max_length=10, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, null=True, upload_to='business_images/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=16)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.business')),
            ],
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('number', models.CharField(max_length=15)),
                ('is_customer', models.BooleanField(default=True)),
                ('is_supplier', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, null=True, upload_to='contact_images/')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.business')),
            ],
        ),
        migrations.CreateModel(
            name='Expense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(blank=True, default='Otros', max_length=100, null=True)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.business')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.card')),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_pro', models.BooleanField(default=False)),
                ('plan', models.CharField(choices=[('gratis', 'Gratis'), ('basico', 'Básico'), ('pro', 'Pro')], default='gratis', max_length=10)),
                ('start_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('expiration_date', models.DateTimeField(default=api.models.get_expiration_date)),
                ('active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('category', models.CharField(blank=True, default='Otros', max_length=100, null=True)),
                ('purchase_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('sale_price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_public', models.BooleanField(default=True)),
                ('stock', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('image', models.ImageField(blank=True, null=True, upload_to='product_images/')),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.business')),
            ],
        ),
        migrations.CreateModel(
            name='Purchase',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('is_credit', models.BooleanField(default=False)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.business')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.card')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.contact')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(blank=True, default=django.utils.timezone.now)),
                ('is_credit', models.BooleanField(default=False)),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.business')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.card')),
                ('contact', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.contact')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.product')),
            ],
        ),
    ]
