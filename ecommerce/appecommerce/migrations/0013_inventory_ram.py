# Generated by Django 5.0.4 on 2024-04-12 10:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appecommerce', '0012_remove_productbasic_brand_name_productbasic_brand'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='ram',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rams', to='appecommerce.variantvalue'),
        ),
    ]
