# Generated by Django 5.0.4 on 2024-04-16 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appecommerce', '0015_paymentcard'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
