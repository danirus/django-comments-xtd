import uuid

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase

from django_comments_xtd.api.frontend import commentbox_props_response, settings
from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Diary, UUIDDiary


class CommentBoxTestCase(TestCase):
    def test_comment_box_props_response(self):
        request_factory = RequestFactory()
        request = request_factory.get("/")
        user = User.objects.create_user("bob", "bob@example.com", "pwd")
        diary = Diary.objects.create(
            body='Lorem ipsum',
            allow_comments=True
        )
        XtdComment.objects.create(
            content_object=diary,
            site_id=1,
        )
        response = commentbox_props_response(diary, user, request)
        d = response.data
        self.assertEqual(d['comment_count'], 1)
        self.assertEqual(d['default_form']['object_pk'], str(diary.id))
        self.assertEqual(d['count_url'], '/comments/api/tests-diary/1/count/')
        self.assertEqual(d['list_url'], '/comments/api/tests-diary/1/')
        self.assertEqual(d['current_user'], "1:bob")
        self.assertEqual(d['comment_max_length'], settings.COMMENT_MAX_LENGTH)

    def test_comment_box_props_response_anonymous(self):
        request_factory = RequestFactory()
        request = request_factory.get("/")
        user = AnonymousUser()
        diary = Diary.objects.create(
            body='Lorem ipsum',
            allow_comments=True
        )
        XtdComment.objects.create(
            content_object=diary,
            site_id=1,
        )
        response = commentbox_props_response(diary, user, request)
        d = response.data
        self.assertEqual(d['comment_count'], 1)
        self.assertEqual(d['default_form']['object_pk'], str(diary.id))
        self.assertEqual(d['count_url'], '/comments/api/tests-diary/1/count/')
        self.assertEqual(d['list_url'], '/comments/api/tests-diary/1/')
        self.assertEqual(d['current_user'], "0:Anonymous")

    def test_comment_box_props_response_uuid(self):
        request_factory = RequestFactory()
        request = request_factory.get("/")
        user = AnonymousUser()
        diary = UUIDDiary.objects.create(
            uuid=uuid.uuid4(),
            body='Lorem ipsum',
            allow_comments=True
        )
        XtdComment.objects.create(
            content_object=diary,
            site_id=1,
        )
        response = commentbox_props_response(diary, user, request)
        d = response.data
        self.assertEqual(d['comment_count'], 1)
        self.assertEqual(d['default_form']['object_pk'], str(diary.uuid))
        self.assertEqual(
            d['count_url'],
            f'/comments/api/tests-uuiddiary/{diary.uuid}/count/'
        )
        self.assertEqual(
            d['list_url'],
            f'/comments/api/tests-uuiddiary/{diary.uuid}/'
        )
