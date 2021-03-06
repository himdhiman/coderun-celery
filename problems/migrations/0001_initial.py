# Generated by Django 3.2.7 on 2021-10-20 08:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Bookmark",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("user", models.EmailField(max_length=150)),
                ("data", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Problem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_by", models.EmailField(max_length=150)),
                ("title", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("problem_statement", models.TextField(blank=True, null=True)),
                ("input_format", models.TextField(blank=True, null=True)),
                ("constraints", models.TextField(blank=True, null=True)),
                ("output_format", models.TextField(blank=True, null=True)),
                (
                    "problem_level",
                    models.CharField(
                        choices=[("E", "Easy"), ("M", "Medium"), ("H", "Hard")],
                        max_length=20,
                    ),
                ),
                ("accuracy", models.IntegerField(default=0)),
                ("totalSubmissions", models.IntegerField(default=0)),
                ("sample_Tc", models.IntegerField(default=0)),
                ("total_Tc", models.IntegerField(default=0)),
                ("created_At", models.DateField(auto_now=True)),
                (
                    "memory_Limit",
                    models.IntegerField(blank=True, default=5120, null=True),
                ),
                ("time_Limit", models.IntegerField(blank=True, default=1, null=True)),
                ("publically_visible", models.BooleanField(default=True)),
                ("approved_by_admin", models.BooleanField(default=False)),
                ("up_votes", models.IntegerField(default=0)),
                ("down_votes", models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="UploadTC",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "testcases",
                    models.FileField(blank=True, null=True, upload_to="tempTC/"),
                ),
                (
                    "name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="problems.problem",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="problem",
            name="tags",
            field=models.ManyToManyField(to="problems.Tag"),
        ),
    ]
