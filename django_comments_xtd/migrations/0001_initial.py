# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_comments', '0002_update_user_email_field_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='XtdComment',
            fields=[
                ('comment_ptr', models.OneToOneField(auto_created=True, primary_key=True, parent_link=True, serialize=False, to='django_comments.Comment', on_delete=models.CASCADE)),
                ('thread_id', models.IntegerField(default=0, db_index=True)),
                ('parent_id', models.IntegerField(default=0)),
                ('level', models.SmallIntegerField(default=0)),
                ('order', models.IntegerField(default=1, db_index=True)),
                ('followup', models.BooleanField(default=False, help_text='Receive by email further comments in this conversation')),
            ],
            options={
                'ordering': ('thread_id', 'order'),
            },
            bases=('django_comments.comment',),
        ),
    ]
