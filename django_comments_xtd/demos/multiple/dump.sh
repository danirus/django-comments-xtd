#!/bin/bash

python manage.py dumpdata --indent 4 --format json -v 2 \
    projects.Project projects.Release \
    blog.Story blog.Quote \
    sites.Site \
    auth.User \
    comments.Comment > initial_data.json

# use this separate fixture to load after migrating django_comments_xtd
python manage.py dumpdata --indent 4 --format json -v 2 \
    django_comments_xtd.XtdComment > fixtures/django_comments_xtd.json
