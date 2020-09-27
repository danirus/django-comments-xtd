from datetime import datetime, timedelta

import django
from django.contrib.auth.models import AnonymousUser, User
from django.test import TestCase, RequestFactory
from django.urls import reverse

from django_comments_xtd import django_comments, views
from django_comments_xtd.models import CommentReaction
from django_comments_xtd.tests.models import Diary
from django_comments_xtd.tests.test_views import post_diary_comment


request_factory = RequestFactory()
comments_model = django_comments.get_model()


class LikedItAndDislikedIt(TestCase):
    """Scenario to test the liked_it/disliked_it comment reaction."""

    def setUp(self):
        diary_entry = Diary.objects.create(
            body="What I did in October...",
            allow_comments=True,
            publish=datetime.now())
        form = django_comments.get_form()(diary_entry)
        self.user = User.objects.create_user("bob", "bob@example.com", "pws")
        data = {"name": "Bob", "email": "bob@example.com", "followup": True,
                "reply_to": 0, "level": 1, "order": 1,
                "comment": "Es war einmail eine kleine..."}
        data.update(form.initial)
        post_diary_comment(data, diary_entry, auth_user=self.user)

    def test_try_to_like_it_as_anonymous_user_gets_redirected(self):
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        # Like it.
        like_url = reverse("comments-xtd-like", args=[comment.id])
        request = request_factory.get(like_url)
        request.user = AnonymousUser()
        response = views.like(request, comment.id)
        dest_url = '/accounts/login/?next=/comments/like/1/'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, dest_url)

    def test_try_to_dislike_it_as_anonymous_user_gets_redirected(self):
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        request = request_factory.get(dislike_url)
        request.user = AnonymousUser()
        response = views.dislike(request, comment.id)
        dest_url = '/accounts/login/?next=/comments/dislike/1/'
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, dest_url)

    def test_try_to_like_it_as_loggedin_user(self):
        if django.VERSION < (1, 5):
            return
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        request = request_factory.get(like_url)
        request.user = self.user
        response = views.like(request, comment.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find(b'value="I like it"') > -1)
        request = request_factory.post(like_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.like(request, comment.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("comments-xtd-like-done") + "?c=1")
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.LIKED_IT)
        self.assertEqual(reactions.count(), 1)

    def test_try_to_dislike_it_as_loggedin_user(self):
        if django.VERSION < (1, 5):
            return
        comment = django_comments.get_model()\
                                 .objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        request = request_factory.get(dislike_url)
        request.user = self.user
        response = views.dislike(request, comment.id)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.content.find(b'value="I dislike it"') > -1)
        request = request_factory.post(dislike_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.dislike(request, comment.id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url, reverse("comments-xtd-dislike-done") + "?c=1")
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.DISLIKED_IT)
        self.assertEqual(reactions.count(), 1)

    def test_liking_a_comment_twice_cancels_the_likeit_reaction(self):
        if django.VERSION < (1, 5):
            return
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        request = request_factory.post(like_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.like(request, comment.id)
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.LIKED_IT)
        self.assertEqual(reactions.count(), 1)
        # By liking the same comment twice we cancel the reaction.
        response = views.like(request, comment.id)
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.LIKED_IT)
        self.assertTrue(reactions.count(), 0)

    def test_disliking_a_comment_twice_cancels_the_dislikeit_reaction(self):
        if django.VERSION < (1, 5):
            return
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        request = request_factory.post(dislike_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.dislike(request, comment.id)
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.DISLIKED_IT)
        self.assertEqual(reactions.count(), 1)
        # By liking the same comment twice we cancel the reaction.
        response = views.dislike(request, comment.id)
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.DISLIKED_IT)
        self.assertTrue(reactions.count(), 0)

    def test_liking_a_comment_after_disliking_it_cancels_the_disliking(self):
        if django.VERSION < (1, 5):
            return
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        request = request_factory.post(dislike_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.dislike(request, comment.id)
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.DISLIKED_IT)
        self.assertEqual(reactions.count(), 1)

        # Now we like the comment and the disliking gets canceled.
        like_url = reverse("comments-xtd-like", args=[comment.id])
        request = request_factory.post(like_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.like(request, comment.id)

        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.DISLIKED_IT)
        self.assertEqual(reactions.count(), 0)

        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.LIKED_IT)
        self.assertEqual(reactions.count(), 1)

    def test_disliking_a_comment_after_liking_it_cancels_the_liking(self):
        if django.VERSION < (1, 5):
            return
        comment = comments_model.objects.for_app_models('tests.diary')[0]
        like_url = reverse("comments-xtd-like", args=[comment.id])
        request = request_factory.post(like_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.like(request, comment.id)
        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.LIKED_IT)
        self.assertEqual(reactions.count(), 1)

        # Now we like the comment and the disliking gets canceled.
        dislike_url = reverse("comments-xtd-dislike", args=[comment.id])
        request = request_factory.post(like_url)
        request.user = self.user
        request._dont_enforce_csrf_checks = True
        response = views.dislike(request, comment.id)

        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.LIKED_IT)
        self.assertEqual(reactions.count(), 0)

        reactions = CommentReaction.objects.filter(
            comment=comment, authors=self.user,
            reaction=CommentReaction.DISLIKED_IT)
        self.assertEqual(reactions.count(), 1)
