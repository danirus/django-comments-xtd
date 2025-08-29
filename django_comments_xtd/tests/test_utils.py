from unittest.mock import MagicMock

import pytest

from django_comments_xtd import utils
from django_comments_xtd.conf.defaults import COMMENTS_XTD_APP_MODEL_OPTIONS


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
    assert utils.mail_sent_queue.get()


@pytest.mark.django_db
def test_send_mail_uses__send_amil(monkeypatch):
    _send_mail_mock = MagicMock()
    monkeypatch.setattr(utils, "_send_mail", _send_mail_mock)
    monkeypatch.setattr(utils.settings, "COMMENTS_XTD_THREADED_EMAILS", False)
    utils.send_mail(
        "the subject",
        "the message",
        "helpdesk@example.com",
        ["fulanito@example.com"],
        html="<p>The message.</p>",
    )
    _send_mail_mock.assert_called()


# ----------------------------------------------
@pytest.mark.django_db
def test_get_app_model_options_without_args():
    options = utils.get_app_model_options()
    assert options == COMMENTS_XTD_APP_MODEL_OPTIONS["default"]


mock_options_settings = {
    "default": {
        # "who_can_post": "all",
        # "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_voting_enabled": True,
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": True,
    },
    "tests.article": {
        "comments_voting_enabled": False,
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": False,
    },
}


@pytest.mark.django_db
def test_get_app_model_options_with_comment(an_articles_comment, monkeypatch):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_APP_MODEL_OPTIONS",
        mock_options_settings,
    )
    options = utils.get_app_model_options(comment=an_articles_comment)
    assert options == {
        "who_can_post": "all",
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_voting_enabled": False,
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": False,
    }


@pytest.mark.django_db
def test_get_app_model_options_with_content_type_None(monkeypatch):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_APP_MODEL_OPTIONS",
        mock_options_settings,
    )
    options = utils.get_app_model_options(content_type=None)
    # Keys 'who_can_post'  and 'check_input_allowed' are not
    # part of mock_options_settings['tests.article'], but we
    # get them in the options from the 'default' key dictionary.
    assert 'who_can_post' in options
    assert 'check_input_allowed' in options
    expected = dict.copy(mock_options_settings["default"])
    expected.update({
        'who_can_post': "all",
        'check_input_allowed': "django_comments_xtd.utils.check_input_allowed"
    })
    assert options == expected


@pytest.mark.django_db
def test_get_app_model_options_with_content_type_valid(
    an_articles_comment, monkeypatch
):
    monkeypatch.setattr(
        utils.settings,
        "COMMENTS_XTD_APP_MODEL_OPTIONS",
        mock_options_settings,
    )
    options = utils.get_app_model_options(
        content_type=an_articles_comment.content_type
    )
    assert options == {  # The options declared above for 'tests.article'
        "who_can_post": "all",
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_voting_enabled": False,
        "comments_flagging_enabled": True,
        "comments_reacting_enabled": False,
    }
