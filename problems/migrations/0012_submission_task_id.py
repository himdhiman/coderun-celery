# Generated by Django 3.2.7 on 2021-12-30 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0011_editorial'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='task_id',
            field=models.TextField(blank=True, null=True),
        ),
    ]
