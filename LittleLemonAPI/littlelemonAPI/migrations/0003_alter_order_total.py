# Generated by Django 5.0 on 2025-07-18 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('littlelemonAPI', '0002_cart'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=6),
        ),
    ]
