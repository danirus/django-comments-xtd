# ruff:noqa: N802
from unittest.mock import MagicMock

import pytest
from django.apps import apps
from django.contrib.contenttypes.models import ContentType

from django_comments_xtd import utils


@pytest.mark.django_db
@pytest.mark.parametrize(
    "app_model, expected_mtl",
    [
        ("tests.diary", 0),  # Explicit 'max_thread_level'.
        ("tests.quote", 3),  # Unspecified, so uses DEFAULT_MAX_THREAD_LEVEL.
        ("tests.article", 3),  # Not listed in MODEL_CONFIG, picks 'default'.
    ],
)
def test_get_max_thread_level(app_model, expected_mtl):
    model = apps.get_model(*app_model.split("."))
    ct = ContentType.objects.get_for_model(model)
    assert utils.get_max_thread_level(ct) == expected_mtl


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
    mocked_send_mail = MagicMock()
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
only_def_cfg = {
    "default": {
        "who_can_post": "all",
        "check_input_allowed": "django_comments_xtd.utils.check_input_allowed",
        "comments_flagging_enabled": True,
        "comments_voting_enabled": True,
        "comments_reacting_enabled": True,
        "max_thread_level": 0,
        "list_order": ("thread__id", "order"),
    }
}


@pytest.mark.django_db
def test_get_app_model_config_without_args_returns_defaults(monkeypatch):
    monkeypatch.setattr(
        utils.settings, "COMMENTS_XTD_APP_MODEL_CONFIG", only_def_cfg
    )
    app_model_options = utils.get_app_model_config()
    assert app_model_options == only_def_cfg["default"]
