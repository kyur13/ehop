# Generated by Django 5.1.6 on 2025-03-03 12:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_blog'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='blog',
            options={'permissions': [('can_publish', 'Can publish blog post')]},
        ),
    ]
