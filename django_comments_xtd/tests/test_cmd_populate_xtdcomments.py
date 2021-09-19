from datetime import datetime
from io import StringIO

from django.db.utils import ConnectionHandler
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.management import call_command
import pytest

from django_comments.models import Comment
from django_comments_xtd.models import XtdComment
from django_comments_xtd.management.commands import populate_xtdcomments


def create_comments(an_article, model=Comment):
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)
    for i in range(5):
        model.objects.create(content_type=article_ct,
                             object_pk=an_article.id,
                             content_object=an_article,
                             comment="Yet another comment",
                             submit_date=datetime.now(),
                             site=site)


@pytest.mark.django_db
def test_populate_xtdcomments(an_article):
    create_comments(an_article)
    output = StringIO()
    call_command('populate_xtdcomments', stdout=output)
    assert output.getvalue() == "Added 5 XtdComment object(s).\n"


@pytest.mark.django_db
def test_populate_xtdcomments_raise_ConnectionDoesNotExist(an_article):
    create_comments(an_article)
    output = StringIO()
    call_command('populate_xtdcomments', 'nondb', stdout=output)
    assert output.getvalue() == ("DB connection 'nondb' does not exist.\n"
                                 "Added 0 XtdComment object(s).\n")


@pytest.mark.django_db
def test_populate_xtdcomments_raise_IntegrityError_1(an_article):
    create_comments(an_article, model=XtdComment)
    output = StringIO()
    call_command('populate_xtdcomments', stdout=output)
    assert output.getvalue() == (
        "Table 'django_comments_xtd_xtdcomment' must be empty.\n"
        "Added 0 XtdComment object(s).\n"
    )
