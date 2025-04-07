from datetime import datetime

import pytest
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article


@pytest.fixture
def an_article():
    """Creates an article that can receive comments."""
    article = Article.objects.create(
        title="September", slug="september", body="During September..."
    )
    yield article
    article.delete()


@pytest.fixture
def an_articles_comment(an_article):
    """Send a comment to the article."""
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)
    comment = XtdComment.objects.create(
        content_type=article_ct,
        object_pk=an_article.pk,
        content_object=an_article,
        site=site,
        comment="First comment to the article.",
        submit_date=datetime.now(),
    )
    yield comment
    comment.delete()
