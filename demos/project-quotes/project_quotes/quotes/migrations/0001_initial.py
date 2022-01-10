# Generated by Django 4.0 on 2022-01-05 19:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('slug', models.SlugField(unique_for_date='published_time', verbose_name='slug')),
                ('quote', models.TextField(verbose_name='quote')),
                ('author', models.CharField(max_length=255, verbose_name='author')),
                ('url_source', models.URLField(blank=True, null=True, verbose_name='url source')),
                ('allow_comments', models.BooleanField(default=True, verbose_name='allow comments')),
                ('published_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='published time')),
            ],
            options={
                'db_table': 'comp_quotes',
                'ordering': ('-published_time',),
            },
        ),
    ]
