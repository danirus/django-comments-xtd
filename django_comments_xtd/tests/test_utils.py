from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.functional import cached_property
import pytest

from django_comments_xtd import get_model, utils
from django_comments_xtd.conf import settings
from django_comments_xtd.conf.defaults import (
    COMMENTS_XTD_APP_MODEL_OPTIONS,
    COMMENTS_XTD_REACTIONS_JS_OVERLAYS,
)
from django_comments_xtd.paginator import CommentsPaginator


XtdComment = get_model()


@pytest.mark.django_db
def test_send_mail_uses_EmailThread(monkeypatch):
    monkeypatch.setattr(utils.settings, "COMMENTS_XTD_THREADED_EMAILS", True)
    utils.send_mail(
        "the subject",
        "the message",
        "helpdesk@example.com",
        ["fulanito@example.com"],
        html="<p>The message.</p>",
    )
    assert utils.mail_sent_queue.get() == True


# ---------------------------------------
send_mail_called = False


def _mocked_send_mail(*args, **kwargs):
    global send_mail_called
    send_mail_called = True


@pytest.mark.django_db
def test_send_mail_uses__send_amil(monkeypatch):
    monkeypatch.setattr(utils, "_send_mail", _mocked_send_mail)
    monkeypatch.setattr(utils.settings, "COMMENTS_XTD_THREADED_EMAILS", False)
    utils.send_mail(
        "the subject",
        "the message",
        "helpdesk@example.com",
        ["fulanito@example.com"],
        html="<p>The message.</p>",
    )
    assert send_mail_called == True


# ----------------------------------------------
@pytest.mark.django_db
def test_get_app_model_options_without_args():
    options = utils.get_app_model_options()
    assert options == COMMENTS_XTD_APP_MODEL_OPTIONS["default"]


# ----------------------------------------------
only_default_options = {
    "default": {
        "who_can_post": "all",
        "check_input_allowed": "",
        "comment_flagging_enabled": True,
        "comment_reactions_enabled": True,
        "object_reactions_enabled": True,
    }
}


@pytest.mark.django_db
def test_get_app_model_options_without_args_returns_defaults(monkeypatch):
    monkeypatch.setattr(
        utils.settings, "COMMENTS_XTD_APP_MODEL_OPTIONS", only_default_options
    )
    app_model_options = utils.get_app_model_options()
    assert app_model_options == only_default_options["default"]


# ----------------------------------------------
default_and_article_options = {
    "default": {
        "who_can_post": "all",
        "check_input_allowed": "",
        "comment_flagging_enabled": True,
        "comment_reactions_enabled": True,
        "object_reactions_enabled": True,
    },
    "tests.article": {
        "comment_flagging_enabled": False,
        "comment_reactions_enabled": False,
        "object_reactions_enabled": False,
    },
}


@pytest.mark.django_db
def test_get_app_model_options_with_comment(an_articles_comment, monkeypatch):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_APP_MODEL_OPTIONS",
        default_and_article_options,
    )
    _options = utils.get_app_model_options(an_articles_comment)
    expected_options = default_and_article_options["default"]
    expected_options.update(default_and_article_options["tests.article"])
    assert _options == expected_options


@pytest.mark.django_db
def test_get_app_model_options_with_content_type(monkeypatch):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_APP_MODEL_OPTIONS",
        default_and_article_options,
    )
    _options = utils.get_app_model_options(content_type="tests.article")
    expected_options = default_and_article_options["default"]
    expected_options.update(default_and_article_options["tests.article"])
    assert _options == expected_options


@pytest.mark.django_db
def test_get_app_model_options_with_non_existing_content_type(monkeypatch):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_APP_MODEL_OPTIONS",
        default_and_article_options,
    )
    _options = utils.get_app_model_options(content_type="tralari.tralara")
    expected_options = default_and_article_options["default"]
    assert _options == expected_options


# ----------------------------------------------
@pytest.mark.django_db
def test_get_reactions_js_overlays_without_args():
    js_overlays = utils.get_reactions_js_overlays()
    assert js_overlays == COMMENTS_XTD_REACTIONS_JS_OVERLAYS["default"]


# ----------------------------------------------
reactions_js_overlays = {
    "default": {
        "popover": {"pos_bottom": 30, "pos_left": 10},
        "tooltip": {"pos_bottom": 30, "pos_left": 76},
    }
}


@pytest.mark.django_db
def test_get_reactions_js_overlays_without_args_returns_defaults(monkeypatch):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_REACTIONS_JS_OVERLAYS",
        reactions_js_overlays,
    )
    result = utils.get_reactions_js_overlays()
    assert result == reactions_js_overlays["default"]


# ----------------------------------------------
@pytest.mark.django_db
def test_get_user_avatar_for_comment(an_articles_comment):
    gravatar_url = utils.get_user_avatar(an_articles_comment)
    assert gravatar_url.startswith("//www.gravatar.com/avatar/")


# ----------------------------------------------
@pytest.mark.django_db
def test_redirect_to_with_comment(an_articles_comment):
    http_response = utils.redirect_to(an_articles_comment)
    assert http_response.url == an_articles_comment.get_absolute_url()


# ----------------------------------------------
class FakeRequest:
    def __init__(self, cpage):
        self.cpage = cpage

    @property
    def GET(self):
        return {"cpage": self.cpage}


@pytest.mark.django_db
def test_redirect_to_with_request(an_articles_comment):
    request = FakeRequest(cpage=2)
    http_response = utils.redirect_to(an_articles_comment, request)
    assert http_response.url == "/comments/cr/10/1/1/?cpage=2#comment-1"


# ----------------------------------------------
@pytest.mark.django_db
def test_redirect_to_with_page_number(an_articles_comment):
    http_response = utils.redirect_to(an_articles_comment, page_number=2)
    assert http_response.url == "/comments/cr/10/1/1/?cpage=2#comment-1"


# ----------------------------------------------
def create_scenario_1(an_article):
    """Test based on the Example 1 of the paginator.py module."""
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)
    attrs = {
        "content_type": article_ct,
        "object_pk": an_article.pk,
        "content_object": an_article,
        "site": site,
        "comment": f"another comment to article {an_article.pk}",
        "submit_date": datetime.now(),
    }

    # Create 8 comments at level 0.
    for cm_level_0 in range(8):
        XtdComment.objects.create(**attrs)

    cmts_level_0 = XtdComment.objects.all()
    # Add the following number of child comments to the previous cmts_level_0.
    children_number = [10, 10, 10, 10, 10, 10, 5, 4]
    for index, cmt_level_0 in enumerate(cmts_level_0):
        for child in range(children_number[index]):
            XtdComment.objects.create(**attrs, parent_id=cmt_level_0.pk)

    return article_ct


@pytest.mark.django_db
def test_get_comment_page_number_when_page_size_is_0(an_article, monkeypatch):
    article_ct = create_scenario_1(an_article)
    monkeypatch.setattr(utils.settings, "COMMENTS_XTD_ITEMS_PER_PAGE", 0)
    for comment in XtdComment.objects.all():
        page_number = utils.get_comment_page_number(
            None, article_ct, an_article.pk, comment.id
        )
        assert page_number == 1


@pytest.mark.django_db
def test_get_comment_page_number(an_article, monkeypatch):
    article_ct = create_scenario_1(an_article)
    monkeypatch.setattr(utils.settings, "SITE_ID", None)
    page_size = 25
    orphans = 10
    assert settings.COMMENTS_XTD_MAX_LAST_PAGE_ORPHANS == orphans
    assert settings.COMMENTS_XTD_ITEMS_PER_PAGE == page_size
    queryset = XtdComment.objects.all()
    paginator = CommentsPaginator(queryset, page_size, orphans)

    page = paginator.page(1)
    for comment in page.object_list:
        page_number = utils.get_comment_page_number(
            None, article_ct, an_article.pk, comment.id
        )
        assert page_number == 1

    page = paginator.page(2)
    for comment in page.object_list:
        page_number = utils.get_comment_page_number(
            None, article_ct, an_article.pk, comment.id
        )
        assert page_number == 2

    page = paginator.page(3)
    for comment in page.object_list:
        page_number = utils.get_comment_page_number(
            None, article_ct, an_article.pk, comment.id
        )
        assert page_number == 3


# -------------------------------------------
class FakeCommentsPaginator(CommentsPaginator):
    @cached_property
    def num_pages(self):
        return 0


@pytest.mark.django_db
def test_get_comment_page_number_raises_Exception(an_article, monkeypatch):
    article_ct = create_scenario_1(an_article)
    monkeypatch.setattr(utils, "CommentsPaginator", FakeCommentsPaginator)
    page_size = 25
    orphans = 10
    assert settings.COMMENTS_XTD_MAX_LAST_PAGE_ORPHANS == orphans
    assert settings.COMMENTS_XTD_ITEMS_PER_PAGE == page_size
    queryset = XtdComment.objects.all()
    paginator = CommentsPaginator(queryset, page_size, orphans)

    page = paginator.page(2)
    comment = page.object_list[0]
    with pytest.raises(Exception):
        utils.get_comment_page_number(
            None, article_ct, an_article.pk, comment.id
        )
