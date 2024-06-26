# Generated by Django 5.0.4 on 2024-04-16 08:56

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appecommerce', '0014_alter_inventory_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentCard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card_number', models.CharField(max_length=16)),
                ('exp_month', models.IntegerField()),
                ('exp_year', models.IntegerField()),
                ('cvc', models.CharField(max_length=3)),
                ('brand', models.CharField(blank=True, max_length=50)),
                ('stripe_card_id', models.CharField(max_length=100)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
