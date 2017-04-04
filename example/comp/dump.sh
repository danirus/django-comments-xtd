python manage.py dumpdata --indent 4 --format json -v 2 \
    articles.Article \
    sites.Site \
    auth.User \
    comments.Comment \
    django_comments_xtd.XtdComment > initial_data.json

