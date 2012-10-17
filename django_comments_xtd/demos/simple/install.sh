#!/bin/bash

python manage.py syncdb --noinput
python manage.py migrate django_comments_xtd
python manage.py loaddata fixtures/django_comments_xtd.json