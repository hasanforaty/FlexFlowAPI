# Generated by Django 4.0.10 on 2024-01-28 05:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0011_node_is_finishing_node'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('histories', models.JSONField()),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
        migrations.AddIndex(
            model_name='history',
            index=models.Index(fields=['content_type', 'object_id'], name='core_histor_content_4ad575_idx'),
        ),
    ]
