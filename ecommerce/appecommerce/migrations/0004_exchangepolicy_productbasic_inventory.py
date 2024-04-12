# Generated by Django 5.0.4 on 2024-04-11 10:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appecommerce', '0003_variant_variantvalue'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ProductBasic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_title', models.CharField(max_length=255)),
                ('product_description', models.TextField()),
                ('brand_name', models.CharField(max_length=100)),
                ('exchange_policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appecommerce.exchangepolicy')),
            ],
        ),
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('promo_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('discount', models.DecimalField(decimal_places=2, max_digits=5)),
                ('quantity', models.PositiveIntegerField()),
                ('product_variant_description', models.CharField(blank=True, max_length=255)),
                ('color', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='colors', to='appecommerce.variantvalue')),
                ('size', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sizes', to='appecommerce.variantvalue')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='appecommerce.productbasic')),
            ],
        ),
    ]
