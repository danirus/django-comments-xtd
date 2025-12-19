from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django_comments.models import CommentFlag

from django_comments_xtd import get_reaction_enum
from django_comments_xtd.models import CommentReaction, XtdComment
from django_comments_xtd.tests.models import Article, Diary, DiaryWithMTL1


@pytest.fixture
def an_article():
    """Creates an article that can receive comments."""
    article = Article.objects.create(
        title="September", slug="september", body="During September..."
    )
    yield article
    article.delete()


@pytest.fixture
def a_diary_entry():
    """Creates a `Diary` instance that can receive comments with MTL 0."""
    entry = Diary.objects.create(body="About today...")
    yield entry
    entry.delete()


@pytest.fixture
def a_diary_with_mtl1():
    """
    Creates a `DiaryWithThreads` instance that can receive comments with MTL 1.
    """
    entry = DiaryWithMTL1.objects.create(body="About today...")
    yield entry
    entry.delete()


@pytest.fixture
def an_user():
    """Add a user to the DB."""
    user = User.objects.create_user(
        "joe", "joe@example.com", "joepwd", first_name="Joe", last_name="Bloggs"
    )
    yield user
    user.delete()


@pytest.fixture
def an_user_2():
    """Add a user2 to the DB."""
    user2 = User.objects.create_user(
        "alice",
        "alice@example.com",
        "alicepwd",
        first_name="Alice",
        last_name="Bloggs",
    )
    yield user2
    user2.delete()


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
        user_email="alice@example.org",
        user_name="Alice Bloggs",
    )
    yield comment
    comment.delete()


@pytest.fixture
def an_articles_comment_removed(an_articles_comment):
    """Mark the comment as removed."""
    an_articles_comment.is_removed = True
    an_articles_comment.save()
    yield an_articles_comment


@pytest.fixture
def a_comments_reaction(an_articles_comment, an_user):
    """Send a comment reaction to a comment."""
    reaction = get_reaction_enum().LIKE_IT
    cmr = CommentReaction.objects.create(
        reaction=reaction, comment=an_articles_comment, counter=1
    )
    cmr.authors.add(an_user)
    cmr.save()
    yield cmr
    cmr.delete()


@pytest.fixture
def a_comments_flag(an_articles_comment, an_user):
    """Send a CommentFlag.SUGGEST_REMOVAL flag to a comment."""
    comment_flag = CommentFlag.objects.create(
        user=an_user,
        comment=an_articles_comment,
        flag=CommentFlag.SUGGEST_REMOVAL,
    )
    yield comment_flag
    comment_flag.delete()
