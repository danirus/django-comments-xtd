try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import unittest

from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase as DjangoTestCase

from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article, Diary
from django_comments_xtd.tests.test_models import (
    thread_test_step_1, thread_test_step_2, thread_test_step_3,
    thread_test_step_4, thread_test_step_5, add_comment_to_diary_entry)


class GetXtdCommentCountTestCase(DjangoTestCase):
    def setUp(self):
        self.article_1 = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.article_2 = Article.objects.create(
            title="October", slug="october", body="What I did on October...")
        self.day_in_diary = Diary.objects.create(body="About Today...")

    def test_get_xtdcomment_count_for_one_model(self):
        thread_test_step_1(self.article_1)
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '2')

    def test_get_xtdcomment_count_for_two_models(self):
        thread_test_step_1(self.article_1)
        add_comment_to_diary_entry(self.day_in_diary)
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname"
             "   for tests.article tests.diary %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '3')


class LastXtdCommentsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.day_in_diary = Diary.objects.create(body="About Today...")
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        add_comment_to_diary_entry(self.day_in_diary)

    def test_render_last_xtdcomments(self):
        t = ("{% load comments_xtd %}"
             "{% render_last_xtdcomments 5 for tests.article tests.diary %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<a name='), 5)
        self.assertEqual(output.count('<a name="c6">'), 1)
        self.assertEqual(output.count('<a name="c5">'), 1)
        self.assertEqual(output.count('<a name="c4">'), 1)
        self.assertEqual(output.count('<a name="c3">'), 1)
        self.assertEqual(output.count('<a name="c2">'), 1)
        # We added 6 comments, and we render the last 5, so
        # the first one must not be rendered in the output.
        self.assertEqual(output.count('<a name="c1">'), 0)

    def test_get_last_xtdcomments(self):
        t = ("{% load comments_xtd %}"
             "{% get_last_xtdcomments 5 as last_comments"
             "   for tests.article tests.diary %}"
             "{% for comment in last_comments %}"
             "<comment>{{ comment.id }}</comment>"
             "{% endfor %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<comment>'), 5)
        self.assertEqual(output.count('<comment>6</comment>'), 1)
        self.assertEqual(output.count('<comment>5</comment>'), 1)
        self.assertEqual(output.count('<comment>4</comment>'), 1)
        self.assertEqual(output.count('<comment>3</comment>'), 1)
        self.assertEqual(output.count('<comment>2</comment>'), 1)
        # We added 6 comments, and we render the last 5, so
        # the first one must not be rendered in the output.
        self.assertEqual(output.count('<comment>1</comment>'), 0)


class XtdCommentsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.day_in_diary = Diary.objects.create(body="About Today...")
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        thread_test_step_4(self.article)
        thread_test_step_5(self.article)

    def _assert_all_comments_are_published(self):
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_tree for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 9)
        # See test_models.py, ThreadStep5TestCase to get a quick
        # view of the comments posted and their thread structure.
        pos_c1 = output.index('<a name="c1"></a>')
        pos_c3 = output.index('<a name="c3"></a>')
        pos_c8 = output.index('<a name="c8"></a>')
        pos_c4 = output.index('<a name="c4"></a>')
        pos_c7 = output.index('<a name="c7"></a>')
        pos_c2 = output.index('<a name="c2"></a>')
        pos_c5 = output.index('<a name="c5"></a>')
        pos_c6 = output.index('<a name="c6"></a>')
        pos_c9 = output.index('<a name="c9"></a>')
        self.assertTrue(pos_c1 > 0)
        self.assertTrue(pos_c3 > 0)
        self.assertTrue(pos_c8 > 0)
        self.assertTrue(pos_c4 > 0)
        self.assertTrue(pos_c7 > 0)
        self.assertTrue(pos_c2 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c9 > 0)
        self.assertTrue(pos_c1 < pos_c3 < pos_c8 <
                        pos_c4 < pos_c7 < pos_c2 <
                        pos_c5 < pos_c6 < pos_c9)

    def test_render_xtdcomment_tree(self):
        self._assert_all_comments_are_published()

    def _assert_only_comment_2_and_3_and_their_children_are_published(self):
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_tree for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 4)
        # Only the following comments must be displayed, the other ones must
        # have been unpublished when setting the comment 1 is_public to False.
        pos_c2 = output.index('<a name="c2"></a>')
        pos_c5 = output.index('<a name="c5"></a>')
        pos_c6 = output.index('<a name="c6"></a>')
        pos_c9 = output.index('<a name="c9"></a>')
        self.assertTrue(pos_c2 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c9 > 0)
        self.assertTrue(pos_c2 < pos_c5 < pos_c6 < pos_c9)

    def test_unpublishing_comment_1(self):
        # Now set comment 1 is_public to False.
        c1 = XtdComment.objects.get(pk=1)
        c1.is_public = False
        # Saving the instance triggers the pre_save signal in the models.py
        # module, which in turn unpublish this comment and all its children.
        c1.save()
        self._assert_only_comment_2_and_3_and_their_children_are_published()

    def test_unpublishing_comment_1_and_publishing_it_again(self):
        # Now set comment 1 is_public to False.
        c1 = XtdComment.objects.get(pk=1)
        c1.is_public = False
        # Saving the instance triggers the pre_save signal in the models.py
        # module, which in turn unpublish this comment and all its children.
        c1.save()
        self._assert_only_comment_2_and_3_and_their_children_are_published()

        c1.is_public = True
        # Saving the instance with is_public = True publish the comment and
        # all the nested comments.
        c1.save()
        self._assert_all_comments_are_published()
