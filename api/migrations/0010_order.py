# Generated by Django 5.1.6 on 2025-02-28 09:59

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_price_range'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='order')),
                ('ord_product', models.CharField(default='', max_length=1000)),
                ('quantity', models.CharField(max_length=5)),
                ('price', models.IntegerField()),
                ('total', models.CharField(default='', max_length=100)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=10)),
                ('pincod', models.CharField(max_length=6)),
                ('date', models.DateField(default=datetime.datetime.today)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
