import pytest

from django_comments_xtd import utils
from django_comments_xtd.conf.defaults import COMMENTS_XTD_APP_MODEL_OPTIONS


@pytest.mark.django_db
def test_send_mail_uses_EmailThread(monkeypatch):
    monkeypatch.setattr(utils.settings, 'COMMENTS_XTD_THREADED_EMAILS', True)
    utils.send_mail("the subject", "the message", "helpdesk@example.com",
                    ["fulanito@example.com"], html="<p>The message.</p>")
    assert utils.mail_sent_queue.get() == True


# ---------------------------------------
send_mail_called = False

def _mocked_send_mail(*args, **kwargs):
    global send_mail_called
    send_mail_called = True

@pytest.mark.django_db
def test_send_mail_uses__send_amil(monkeypatch):
    monkeypatch.setattr(utils, '_send_mail', _mocked_send_mail)
    monkeypatch.setattr(utils.settings, 'COMMENTS_XTD_THREADED_EMAILS', False)
    utils.send_mail("the subject", "the message", "helpdesk@example.com",
                    ["fulanito@example.com"], html="<p>The message.</p>")
    assert send_mail_called == True


# ----------------------------------------------
@pytest.mark.django_db
def test_get_app_model_options_without_args():
    options = utils.get_app_model_options()
    assert options == COMMENTS_XTD_APP_MODEL_OPTIONS['default']


# ----------------------------------------------
only_default_options = {
    'default': {
        'who_can_post': 'all',
        'check_input_allowed': '',
        'comment_flagging_enabled': True,
        'comment_reactions_enabled': True,
        'object_reactions_enabled': True
    }
}


@pytest.mark.django_db
def test_get_app_model_options_without_args_returns_defaults(monkeypatch):
    monkeypatch.setattr(utils.settings, 'COMMENTS_XTD_APP_MODEL_OPTIONS',
                        only_default_options)
    app_model_options = utils.get_app_model_options()
    assert app_model_options == only_default_options['default']


# ----------------------------------------------
default_and_article_options = {
    'default': {
        'who_can_post': 'all',
        'check_input_allowed': '',
        'comment_flagging_enabled': True,
        'comment_reactions_enabled': True,
        'object_reactions_enabled': True
    },
    'tests.article': {
        'comment_flagging_enabled': False,
        'comment_reactions_enabled': False,
        'object_reactions_enabled': False
    }
}


@pytest.mark.django_db
def test_get_app_model_options_with_comment(an_articles_comment, monkeypatch):
    monkeypatch.setattr(utils.settings, 'COMMENTS_XTD_APP_MODEL_OPTIONS',
                        default_and_article_options)
    _options = utils.get_app_model_options(an_articles_comment)
    expected_options = default_and_article_options['default']
    expected_options.update(default_and_article_options['tests.article'])
    assert _options == expected_options


@pytest.mark.django_db
def test_get_app_model_options_with_content_type(monkeypatch):
    monkeypatch.setattr(utils.settings, 'COMMENTS_XTD_APP_MODEL_OPTIONS',
                        default_and_article_options)
    _options = utils.get_app_model_options(content_type="tests.article")
    expected_options = default_and_article_options['default']
    expected_options.update(default_and_article_options['tests.article'])
    assert _options == expected_options
