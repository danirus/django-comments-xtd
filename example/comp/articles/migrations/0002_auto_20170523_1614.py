# Generated by Django 1.11.1 on 2017-05-23 14:14

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article",
            name="publish",
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name="publish"
            ),
        ),
    ]
