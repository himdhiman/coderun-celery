# Generated by Django 3.2.7 on 2021-12-29 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("problems", "0010_alter_problem_memory_limit"),
    ]

    operations = [
        migrations.CreateModel(
            name="Editorial",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("problem_Id", models.IntegerField(blank=True, null=True)),
                ("cpp17", models.TextField(blank=True, null=True)),
                ("java", models.TextField(blank=True, null=True)),
                ("python2", models.TextField(blank=True, null=True)),
                ("python3", models.TextField(blank=True, null=True)),
                ("cpp14", models.TextField(blank=True, null=True)),
                ("c", models.TextField(blank=True, null=True)),
            ],
        ),
    ]
