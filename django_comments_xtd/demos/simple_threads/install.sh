#!/bin/bash

# use this script only when 'south' is active in INSTALLED_APPS
# otherwise do just the 'syncdb --noinput'

python manage.py syncdb --noinput
python manage.py migrate django_comments_xtd
python manage.py loaddata fixtures/django_comments_xtd.json