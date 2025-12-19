from unittest.mock import Mock

import pytest
from django.contrib.contenttypes.models import ContentType

from django_comments_xtd import utils
from django_comments_xtd.tests import models


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
    assert utils.mail_sent_queue.get() is True


@pytest.mark.django_db
def test_send_mail_uses__send_mail(monkeypatch):
    mocked_send_mail = Mock()
    monkeypatch.setattr(utils, "_send_mail", mocked_send_mail)
    monkeypatch.setattr(utils.settings, "COMMENTS_XTD_THREADED_EMAILS", False)
    utils.send_mail(
        "the subject",
        "the message",
        "helpdesk@example.com",
        ["fulanito@example.com"],
        html="<p>The message.</p>",
    )
    assert mocked_send_mail.called is True
    assert mocked_send_mail.call_args[0] == (
        "the subject",
        "the message",
        "helpdesk@example.com",
        ["fulanito@example.com"],
        False,  # fail_silently
        "<p>The message.</p>",  # html
    )


# ----------------------------------------------------------------------
only_def_cfg = {
    "default": {
        "who_can_post": "all",
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_flagging_enabled": True,
        "comments_voting_enabled": True,
        "comments_reacting_enabled": True,
        "max_thread_level": 1,
        "list_order": ("-thread__id", "order"),
    }
}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "app_model, override, expected",
    [
        ("tests.diary", False, 0),
        ("tests.article", False, 3),
        (None, False, 3),  # from COMMENTS_XTD_DEFAULT_MAX_THREAD_LEVEL.
        (None, True, 1),  # from above `only_def_cfg`.
    ],
)
def test_get_max_thread_level(app_model, override, expected, monkeypatch):
    if override:
        monkeypatch.setattr(
            utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", only_def_cfg
        )
    if app_model:
        app_label, model = app_model.split(".")
        ctype = ContentType.objects.get(app_label=app_label, model=model)
    else:
        ctype = None
    result = utils.get_max_thread_level(ctype)
    assert result == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "app_model, override, expected",
    [
        ("tests.quote", False, ("-thread__score", "thread__id", "order")),
        ("tests.article", False, ("thread__id", "order")),
        (None, False, ("thread__id", "order")),
        (None, True, ("-thread__id", "order")),  # from above `only_def_cfg`.
    ],
)
def test_get_list_order(app_model, override, expected, monkeypatch):
    if override:
        monkeypatch.setattr(
            utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", only_def_cfg
        )
    if app_model:
        app_label, model = app_model.split(".")
        ctype = ContentType.objects.get(app_label=app_label, model=model)
    else:
        ctype = None
    result = utils.get_list_order(ctype)
    assert result == expected


# ----------------------------------------------------------------------
@pytest.mark.django_db
def test_get_app_model_config_without_args():
    options = utils.get_app_model_config()
    assert options == {
        "who_can_post": "all",
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": False,
        "comments_voting_enabled": False,
        "max_thread_level": 0,
        "list_order": ("thread__id", "order"),
    }


# ----------------------------------------------------------------------
@pytest.mark.django_db
def test_get_app_model_config_without_args_returns_defaults(monkeypatch):
    monkeypatch.setattr(
        utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", only_def_cfg
    )
    app_model_options = utils.get_app_model_config()
    assert app_model_options == only_def_cfg["default"]


# ----------------------------------------------------------------------
default_and_article_cfg = {
    "default": {
        "who_can_post": "all",
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": True,
        "comments_voting_enabled": True,
        "max_thread_level": 0,
        "list_order": ("thread__id", "order"),
    },
    "tests.article": {
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": True,
        "comments_voting_enabled": True,
    },
}


@pytest.mark.django_db
def test_get_app_model_config_with_comment(an_articles_comment, monkeypatch):
    monkeypatch.setattr(
        utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", default_and_article_cfg
    )
    _config = utils.get_app_model_config(comment=an_articles_comment)
    expected_config = default_and_article_cfg["default"]
    expected_config.update(default_and_article_cfg["tests.article"])
    assert _config == expected_config


@pytest.mark.django_db
def test_get_app_model_options_with_content_type(monkeypatch):
    monkeypatch.setattr(
        utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", default_and_article_cfg
    )
    ctype = ContentType.objects.get_for_model(models.Article)
    _config = utils.get_app_model_config(content_type=ctype)
    expected_config = default_and_article_cfg["default"]
    expected_config.update(default_and_article_cfg["tests.article"])
    assert _config == expected_config


@pytest.mark.django_db
def test_get_app_model_options_with_content_type_None(monkeypatch):
    monkeypatch.setattr(
        utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", default_and_article_cfg
    )
    _config = utils.get_app_model_config(content_type=None)
    expected_config = default_and_article_cfg["default"]
    assert _config == expected_config


# ----------------------------------------------------------------------
def test_get_html_id_suffix(monkeypatch):
    salted_hmac_result_mock = Mock()
    salted_hmac_result_mock.configure_mock(
        **{"hexdigest.return_value": "a salted hmac in hex"}
    )
    salted_hmac_mock = Mock(return_value=salted_hmac_result_mock)
    monkeypatch.setattr(utils, "salted_hmac", salted_hmac_mock)
    result = utils.get_html_id_suffix("a string")
    assert result == "a salted hmac in hex"
    assert salted_hmac_mock.called
    assert salted_hmac_result_mock.hexdigest.called


@pytest.mark.django_db
def test_get_user_gravatar_for_comment(an_articles_comment):
    gravatar_url = utils.get_user_gravatar(an_articles_comment)
    assert gravatar_url.startswith("//www.gravatar.com/avatar/")


@pytest.mark.django_db
def test_redirect_to_with_comment(an_articles_comment):
    http_response = utils.redirect_to(an_articles_comment)
    assert http_response.url == an_articles_comment.get_absolute_url()
