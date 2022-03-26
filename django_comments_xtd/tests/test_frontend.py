import json

import pytest
from django.contrib.auth.models import AnonymousUser, Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from django_comments.models import Comment

from django_comments_xtd import utils
from django_comments_xtd.api import frontend
from django_comments_xtd.conf import settings

from django_comments_xtd.models import max_thread_level_for_content_type


@pytest.mark.django_db
def test_comment_box_props_with_object_and_user(an_user, an_article):
    """
    Verify the default props obtained for an_article without comments.
    """
    props = frontend.comments_api_props(an_article, an_user)

    ctype = ContentType.objects.get_for_model(an_article)
    ctype_slug = "%s-%s" % (ctype.app_label, ctype.model)

    # Verify that the props dictionary contains a form dictionary
    # with the same keys as the CommentSecurityForm.
    assert "content_type" in props["form"]
    assert "object_pk" in props["form"]
    assert "timestamp" in props["form"]
    assert "security_hash" in props["form"]

    assert props["comment_count"] == 0
    assert props["input_allowed"] == True
    assert props["current_user"] == "1:joe"
    assert props["request_name"] == False  # an_user.get_full_name() != "".
    assert props["request_email_address"] == False  # an_user.email != None.
    assert props["is_authenticated"] == True
    assert props["who_can_post"] == "all"
    assert props["comment_flagging_enabled"] == False
    assert props["comment_reactions_enabled"] == False
    assert props["object_reactions_enabled"] == False
    assert props["can_moderate"] == False
    assert props["react_url"] == reverse("comments-xtd-api-react")
    assert props["delete_url"] == reverse("comments-delete", args=(0,))
    assert props["reply_url"] == reverse(
        "comments-xtd-reply", kwargs={"cid": 0}
    )
    assert props["flag_url"] == reverse("comments-xtd-api-flag")
    assert props["list_url"] == reverse(
        "comments-xtd-api-list",
        kwargs={"content_type": ctype_slug, "object_pk": an_article.id},
    )
    assert props["count_url"] == reverse(
        "comments-xtd-api-count",
        kwargs={"content_type": ctype_slug, "object_pk": an_article.id},
    )
    assert props["send_url"] == reverse("comments-xtd-api-create")
    assert props["default_followup"] == settings.COMMENTS_XTD_DEFAULT_FOLLOWUP
    assert props["html_id_suffix"] == utils.get_html_id_suffix(an_article)
    assert props["max_thread_level"] == max_thread_level_for_content_type(ctype)


def check_input_allowed(object):
    return False


@pytest.mark.django_db
def test_comment_box_props_with_new_app_model_options(
    an_user, an_article, monkeypatch
):
    """
    Modify setting COMMENTS_XTD_APP_MODEL_OPTIONS to contain an entry for
    'check_input_allowed' pointing to a function that will return False. The
    dictionary returned by comments_api_props must have a key 'input_allowed' with a False value. Also modify the rest of the values provided by the
    setting to check that comments_api_props reads them correctly.
    """
    check_f = "django_comments_xtd.tests.test_frontend.check_input_allowed"
    app_model_options = {
        "who_can_post": "users",
        "check_input_allowed": check_f,
        "comment_flagging_enabled": True,
        "comment_reactions_enabled": True,
        "object_reactions_enabled": True,
    }
    monkeypatch.setattr(
        frontend, "get_app_model_options", lambda **kwargs: app_model_options
    )
    props = frontend.comments_api_props(an_article, an_user)
    assert props["input_allowed"] == False
    assert props["who_can_post"] == "users"
    assert props["comment_flagging_enabled"] == True
    assert props["comment_reactions_enabled"] == True
    assert props["object_reactions_enabled"] == True


@pytest.mark.django_db
def test_comment_box_props_with_new_max_thread_level(
    an_user, an_article, monkeypatch
):
    monkeypatch.setattr(
        frontend, "max_thread_level_for_content_type", lambda *args: 1
    )
    props = frontend.comments_api_props(an_article, an_user)
    assert props["max_thread_level"] == 1


@pytest.mark.django_db
def test_comment_box_props_with_anonymous_user(an_article):
    anonymous_user = AnonymousUser()
    props = frontend.comments_api_props(an_article, anonymous_user)
    assert props["current_user"] == "0:Anonymous"
    assert props["is_authenticated"] == False
    assert "login_url" in props
    assert props["login_url"] == settings.LOGIN_URL


@pytest.mark.django_db
def test_comment_box_props_with_user_that_can_moderate(an_user, an_article):
    ct_comments = ContentType.objects.get_for_model(Comment)
    can_moderate = Permission.objects.get(
        codename="can_moderate", content_type=ct_comments
    )
    an_user.user_permissions.add(can_moderate)
    props = frontend.comments_api_props(an_article, an_user)
    assert props["can_moderate"] == True


@pytest.mark.django_db
def test_comment_box_props_response(an_user, an_article):
    from rest_framework.response import Response

    response = frontend.comments_api_props_response(
        an_article, an_user, request=None
    )
    props = frontend.comments_api_props(an_article, an_user)
    assert isinstance(response, Response)
    assert response.data == props
