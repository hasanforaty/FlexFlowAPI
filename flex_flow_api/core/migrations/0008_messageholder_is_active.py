# Generated by Django 4.0.10 on 2024-01-24 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_messageholder'),
    ]

    operations = [
        migrations.AddField(
            model_name='messageholder',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
