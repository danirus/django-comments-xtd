import json
from datetime import datetime
from unittest.mock import patch

import django_comments
import pytest
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db.models.signals import pre_save
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from django.utils.text import slugify
from rest_framework import status
from rest_framework.test import (
    APIRequestFactory,
    APITestCase,
    force_authenticate,
)

from django_comments_xtd import get_model
from django_comments_xtd.api import views
from django_comments_xtd.conf import settings
from django_comments_xtd.models import (
    publish_or_withhold_on_pre_save,
)
from django_comments_xtd.tests import views as tviews
from django_comments_xtd.tests.models import Article, MyComment
from django_comments_xtd.tests.test_models import (
    thread_test_step_1,
    thread_test_step_2,
    thread_test_step_3,
)
from django_comments_xtd.tests.utils import post_comment

app_model_config_mock = {"tests.article": {"who_can_post": "users"}}

factory = APIRequestFactory()


class CommentCreateTestCase(DjangoTestCase):
    def setUp(self):
        self.patcher = patch("django_comments_xtd.views.utils.send_mail")
        self.mock_mailer = self.patcher.start()
        self.article = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.form = django_comments.get_form()(self.article)

    def tearDown(self):
        self.patcher.stop()

    @patch.multiple(
        "django_comments_xtd.conf.settings", COMMENTS_XTD_CONFIRM_EMAIL=False
    )
    def test_post_returns_201_response(self):
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.rendered_content)
        self.assertTrue("id" in data)
        self.assertEqual(data["id"], 1)  # id of the new created comment.

    def test_post_returns_2xx_response(self):
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.mock_mailer.call_count, 1)

    def test_post_returns_4xx_response(self):
        # It uses an authenticated user, but the user has no mail address.
        self.user = User.objects.create_user("bob", "", "pwd")
        data = {
            "name": "",
            "email": "",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data, auth_user=self.user)
        self.assertEqual(response.status_code, 400)
        self.assertTrue("name" in response.data)
        self.assertTrue("email" in response.data)
        self.assertEqual(self.mock_mailer.call_count, 0)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_APP_MODEL_CONFIG=app_model_config_mock,
    )
    def test_post_returns_unauthorize_response(self):
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": 0,
            "level": 1,
            "order": 1,
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.rendered_content, b'"User not authenticated"')
        self.assertEqual(self.mock_mailer.call_count, 0)

    def post_parent_comment(self):
        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site1 = Site.objects.get(pk=1)
        self.cm = get_model().objects.create(
            content_type=article_ct,
            object_pk=self.article.id,
            content_object=self.article,
            site=site1,
            comment="just a testing comment",
            submit_date=datetime.now(),
        )

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_CONFIRM_EMAIL=False,
        COMMENTS_XTD_DEFAULT_MAX_THREAD_LEVEL=0,
    )
    def test_post_reply_to_exceeds_max_thread_level_returns_400_code(self):
        self.assertEqual(settings.COMMENTS_XTD_DEFAULT_MAX_THREAD_LEVEL, 0)
        self.assertEqual(get_model().objects.count(), 0)
        self.post_parent_comment()
        self.assertEqual(get_model().objects.count(), 1)
        data = {
            "name": "Bob",
            "email": "fulanito@detal.com",
            "followup": True,
            "reply_to": self.cm.id,  # This exceeds max thread level.
            "comment": "Es war einmal eine kleine...",
            "honeypot": "",
        }
        data.update(self.form.initial)
        response = post_comment(data)
        self.assertEqual(get_model().objects.count(), 1)  # Comment not added.
        self.assertEqual(response.status_code, 400)


_cm_model = "django_comments_xtd.tests.models.MyComment"


class CommentCountTestCase(APITestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September..."
        )

    def _send_request(self):
        kwargs = {"content_type": "tests-article", "object_pk": "1"}
        req = factory.get(reverse("comments-xtd-api-count", kwargs=kwargs))
        view = views.CommentCount.as_view()
        return view(req, **kwargs)

    def test_get_count_shall_be_0(self):
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":0}')

    def test_get_count_shall_be_2(self):
        thread_test_step_1(self.article)
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple(
        "django_comments_xtd.conf.settings", COMMENTS_XTD_MODEL=_cm_model
    )
    def test_get_count_for_custom_comment_model_shall_be_2(self):
        thread_test_step_1(
            self.article, model=MyComment, title="Can't be empty 1"
        )
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple("django_comments_xtd.conf.settings", SITE_ID=2)
    def test_get_count_for_comments_sent_to_different_site(self):
        site2 = Site.objects.create(domain="site2.com", name="site2.com")
        thread_test_step_1(self.article)
        thread_test_step_1(self.article, site=site2)
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_HIDE_REMOVED=True,
        COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True,
    )
    def test_get_count_for_HIDE_REMOVED_case_1(self):
        # To find out what are the cases 1, 2 and 3, read the docs settings
        # page, section COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED.
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # Previous two lines create the following comments:
        #  content ->    cmt.id  thread_id  parent_id  level  order
        #   cm1,   ->     1         1          1        0      1
        #   cm3,   ->     3         1          1        1      2
        #   cm4,   ->     4         1          1        1      3
        #   cm2,   ->     2         2          2        0      1
        cm1 = get_model().objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False.
        # Therefore the count should return 1 -> cm2. cm1 is hidden.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":1}')

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_HIDE_REMOVED=False,
        COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True,
    )
    def test_get_count_for_HIDE_REMOVED_case_2(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()
        #
        cm1 = get_model().objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":2}')

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_HIDE_REMOVED=False,
        COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False,
    )
    def test_get_count_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(
            publish_or_withhold_on_pre_save, sender=model_app_label
        )
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        #
        # These two lines create the following comments:
        #
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()

        cm1 = get_model().objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 must remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.rendered_content, b'{"count":4}')

        # Re-connect the function for the following tests.
        pre_save.connect(
            publish_or_withhold_on_pre_save, sender=model_app_label
        )


class CommentListTestCase(APITestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September..."
        )

    def _send_request(self):
        kwargs = {"content_type": "tests-article", "object_pk": "1"}
        req = factory.get(reverse("comments-xtd-api-list", kwargs=kwargs))
        view = views.CommentList.as_view()
        return view(req, **kwargs)

    def test_get_list(self):
        thread_test_step_1(self.article)  # Sends 2 comments.
        thread_test_step_2(self.article)  # Sends 2 comments.
        thread_test_step_3(self.article)  # Sends 1 comment.
        # -> content:   cmt.id  thread_id  parent_id  level  order
        # cm1,   # ->      1         1          1        0      1
        # cm3,   # ->      3         1          1        1      2
        # cm4,   # ->      4         1          1        1      3
        # cm2,   # ->      2         2          2        0      1
        # cm5    # ->      5         2          2        1      2
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 5)
        for cm, cm_id in zip(data, [1, 3, 4, 2, 5], strict=True):
            self.assertEqual(cm["id"], cm_id)

    # Missing enhancement: extend the capacity to customize the comment model
    # to the API, so that a comment model can be used in combination with its
    # own serializer, and test it here.

    @patch.multiple("django.conf.settings", SITE_ID=2)
    def test_get_list_for_a_second_site(self):
        site2 = Site.objects.create(domain="site2.com", name="site2.com")

        # Send nested comments to the article in the site1.
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)

        # Send some nested comments to the article in the site2.
        thread_test_step_1(self.article, site=site2)

        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 2)
        for cm, cm_id in zip(data, [6, 7], strict=True):
            self.assertEqual(cm["id"], cm_id)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True,
        COMMENTS_HIDE_REMOVED=True,
    )
    def test_get_list_for_HIDE_REMOVED_case_1(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # Previous two lines create the following comments:
        #  content ->    cmt.id  thread_id  parent_id  level  order
        #   cm1,   ->     1         1          1        0      1
        #   cm3,   ->     3         1          1        1      2
        #   cm4,   ->     4         1          1        1      3
        #   cm2,   ->     2         2          2        0      1
        cm1 = get_model().objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing cm1, both cm3 and cm4 have is_public=False.
        # Therefore the list of comments should contain only cm2.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], 2)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True,
        COMMENTS_HIDE_REMOVED=False,
    )
    def test_get_list_for_HIDE_REMOVED_case_2(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()
        #
        cm1 = get_model().objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 2)
        for cm, cm_id in zip(data, [1, 2], strict=True):
            self.assertEqual(cm["id"], cm_id)

    @patch.multiple(
        "django_comments_xtd.conf.settings",
        COMMENTS_HIDE_REMOVED=False,
        COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False,
    )
    def test_get_list_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(
            publish_or_withhold_on_pre_save, sender=model_app_label
        )
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()
        cm1 = get_model().objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        resp = self._send_request()
        self.assertEqual(resp.status_code, 200)
        data = json.loads(resp.rendered_content)
        self.assertEqual(len(data), 4)
        for cm, cm_id in zip(data, [1, 3, 4, 2], strict=True):
            self.assertEqual(cm["id"], cm_id)
        # Re-connect the function for the following tests.
        pre_save.connect(
            publish_or_withhold_on_pre_save, sender=model_app_label
        )


@pytest.mark.django_db
def test_CommentList_handles_no_ContentType():
    kwargs = {"content_type": "this-that", "object_pk": "1"}
    request = factory.get(reverse("comments-xtd-api-list", kwargs=kwargs))
    view = views.CommentList.as_view()
    response = view(request, **kwargs)
    assert response.status_code == status.HTTP_200_OK
    assert response.rendered_content == b"[]"


@pytest.mark.django_db
def test_CommentCount_settings_has_no_SITE_ID(monkeypatch):
    # Remove 'SITE_ID' from settings module, to test that method 'get_queryset'
    # in CommentCount class uses function 'utils.get_current_site_id' to get
    # the site_id.
    monkeypatch.delattr(settings, name="SITE_ID")
    kwargs = {"content_type": "tests-article", "object_pk": "1"}
    request = factory.get(reverse("comments-xtd-api-count", kwargs=kwargs))
    view = views.CommentCount.as_view()
    response = view(request, **kwargs)
    assert response.status_code == status.HTTP_200_OK
    assert response.rendered_content == b'{"count":0}'


# ---------------------------------------------------------------------
@pytest.mark.django_db
def test_PostCommentReaction_raises_403(an_articles_comment, an_user):
    data = {"reaction": "+", "comment": an_articles_comment.pk}
    request = factory.post(reverse("comments-xtd-api-react"), data)
    force_authenticate(request, user=an_user)
    view = views.PostCommentReaction.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_PostCommentReaction_does_work(
    monkeypatch, an_articles_comment, an_user
):
    monkeypatch.setattr(views, "check_option", lambda *x, **y: True)
    data = {"reaction": "+", "comment": an_articles_comment.pk}
    request = factory.post(reverse("comments-xtd-api-react"), data)
    force_authenticate(request, user=an_user)
    view = views.PostCommentReaction.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED


# ---------------------------------------------------------------------
def _send_reaction(data, user):
    request = factory.post(reverse("comments-xtd-api-react"), data)
    force_authenticate(request, user=user)
    view = views.PostCommentReaction.as_view()
    response = view(request)
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
@pytest.mark.parametrize("remap_url", [False, True])
def test_CommentReactionAuthorsList(
    remap_url, monkeypatch, an_articles_comment
):
    """
    Create N+1 users and send the same reaction to `an_articles_comment`.
    Then checks that the API view `CommentReactionAuthorsList` returns as
    much as `COMMENTS_XTD_REACTION_AUTHORS_PER_PAGE` authors per page.
    They come sorted by COMMENTS_XTD_REACTION_AUTHORS_LIST_ORDER, which
    by default is `("-id",)`.
    When remap_url is True, the test uses an alternative view for dcx's API
    URL `comments-xtd-comment-reaction-authors` that eliminates pagination.
    No need for the `DefaultsMixin` class from dcx v2.
    """
    data = {"reaction": "+", "comment": an_articles_comment.pk}
    request = factory.post(reverse("comments-xtd-api-react"), data)
    monkeypatch.setattr(views, "check_option", lambda *x, **y: True)
    total_comment_reactions = 0

    name_ptn = "Isabel Number{number}"
    expected_author_list = []
    total_per_page = settings.COMMENTS_XTD_REACTION_AUTHORS_PER_PAGE

    # Create as many reactions as authors in total_per_page + 1, so that we
    # can check whether there is pagination (or there isn't: remap_url=True).
    for i in range(total_per_page + 1):
        name = name_ptn.format(number=i).split(" ")
        first_name, last_name = name
        user = User.objects.create_user(
            slugify(name),
            f"{slugify(name)}@example.com",
            "pwd",
            first_name=first_name,
            last_name=last_name,
        )
        _send_reaction(data, user)
        expected_author_list.append({"id": user.id, "author": user.username})
        total_comment_reactions += 1

    kwargs = {
        "comment_pk": an_articles_comment.pk,
        "reaction_value": "+",
    }
    if remap_url:
        with patch(
            "django_comments_xtd.conf.settings",
            ROOT_URLCONF="django_comments_xtd.tests.urls_alt",
        ):
            request = factory.get(
                reverse("comments-xtd-comment-reaction-authors", kwargs=kwargs)
            )
            view = tviews.AltCommentReactionAuthorsList.as_view()
            response = view(request, **kwargs)
    else:
        request = factory.get(
            reverse("comments-xtd-comment-reaction-authors", kwargs=kwargs)
        )
        view = views.CommentReactionAuthorsList.as_view()
        response = view(request, **kwargs)

    assert response.status_code == status.HTTP_200_OK
    data = json.loads(response.rendered_content)
    if remap_url:
        assert "count" not in data  # Alternartive view disables pagination.
    else:
        assert "count" in data
        assert data["count"] == total_comment_reactions  # Number of reactions.
        assert len(data["results"]) == total_per_page

    authors_data_page = sorted(
        expected_author_list, key=lambda item: item["id"], reverse=True
    )

    if remap_url:
        assert data == authors_data_page
    else:
        assert data["results"] == authors_data_page[:total_per_page]


@pytest.mark.django_db
def test_CommentReactionAuthorsList_may_be_empty(an_articles_comment):
    kwargs = {
        "comment_pk": an_articles_comment.pk,
        "reaction_value": "+",
    }
    request = factory.get(
        reverse("comments-xtd-comment-reaction-authors", kwargs=kwargs)
    )
    view = views.CommentReactionAuthorsList.as_view()
    response = view(request, **kwargs)
    data = json.loads(response.rendered_content)
    assert response.status_code == status.HTTP_200_OK
    assert "count" in data
    assert data["count"] == 0
    assert "results" in data
    assert data["results"] == []
