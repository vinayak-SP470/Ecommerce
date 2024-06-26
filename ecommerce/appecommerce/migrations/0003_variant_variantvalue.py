# Generated by Django 5.0.4 on 2024-04-11 09:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appecommerce', '0002_brand_productcategory_widget'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='VariantValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='appecommerce.variant')),
            ],
        ),
    ]
