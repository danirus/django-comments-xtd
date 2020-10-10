try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import unittest

from django.db.models.signals import pre_save
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase as DjangoTestCase

from django_comments_xtd import get_model
from django_comments_xtd.models import (
    XtdComment, publish_or_withhold_on_pre_save)
from django_comments_xtd.tests.models import Article, Diary, MyComment
from django_comments_xtd.tests.test_models import (
    thread_test_step_1, thread_test_step_2, thread_test_step_3,
    thread_test_step_4, thread_test_step_5, add_comment_to_diary_entry)


_xtd_model = "django_comments_xtd.tests.models.MyComment"


class GetXtdCommentCountTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.day_in_diary = Diary.objects.create(body="About Today...")

    def test_get_xtdcomment_count_for_one_model(self):
        thread_test_step_1(self.article)
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '2')

    def test_get_xtdcomment_count_for_two_models(self):
        thread_test_step_1(self.article)
        add_comment_to_diary_entry(self.day_in_diary)
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname"
             "   for tests.article tests.diary %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '3')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MODEL=_xtd_model)
    def test_get_xtdcomment_count_for_xtdcomment_model(self):
        thread_test_step_1(self.article, model=MyComment,
                           title="Can't be empty 1")
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '2')

    @patch.multiple('django_comments_xtd.conf.settings', SITE_ID=2)
    def test_get_xtdcomment_count_for_one_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')
        thread_test_step_1(self.article)  # Creates 2 comments in site1.
        thread_test_step_1(self.article, site=site2)  # Creates 2 comments.
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '2')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_xtdcomment_count_for_HIDE_REMOVED_case_1(self):
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
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False.
        # Therefore the count should return 1 -> cm2. cm1 is hidden.
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '1')

        (cm1, cm3, cm4, cm2) = XtdComment.objects.all()
        # Comment 1 is public, but is also removed.
        self.assertEqual(cm1.id, 1)
        self.assertEqual(cm1.is_public, True)
        self.assertEqual(cm1.is_removed, True)
        # Comment 2 is public, and not removed.
        self.assertEqual(cm2.id, 2)
        self.assertEqual(cm2.is_public, True)
        self.assertEqual(cm2.is_removed, False)
        # Comment 3 and 4 are not public, but not removed.
        for cm in [cm3, cm4]:
            self.assertEqual(cm.is_public, False)
            self.assertEqual(cm.is_removed, False)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_xtdcomment_count_for_HIDE_REMOVED_case_2(self):
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
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()

        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '2')

        (cm1, cm3, cm4, cm2) = XtdComment.objects.all()
        # Comment 1 is public, but is also removed.
        self.assertEqual(cm1.id, 1)
        self.assertEqual(cm1.is_public, True)
        self.assertEqual(cm1.is_removed, True)
        # Comment 2 is public, and not removed.
        self.assertEqual(cm2.id, 2)
        self.assertEqual(cm2.is_public, True)
        self.assertEqual(cm2.is_removed, False)
        # Comment 3 and 4 are not public, but not removed.
        for cm in [cm3, cm4]:
            self.assertEqual(cm.is_public, False)
            self.assertEqual(cm.is_removed, False)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False)
    def test_get_xtdcomment_count_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(publish_or_withhold_on_pre_save,
                            sender=model_app_label)
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

        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()

        # After removing the cm1, both cm3 and cm4 must remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        t = ("{% load comments_xtd %}"
             "{% get_xtdcomment_count as varname for tests.article %}"
             "{{ varname }}")
        self.assertEqual(Template(t).render(Context()), '4')

        (cm1, cm3, cm4, cm2) = XtdComment.objects.all()
        # Comment 1 is public, but is also removed.
        self.assertEqual(cm1.id, 1)
        self.assertEqual(cm1.is_public, True)
        self.assertEqual(cm1.is_removed, True)
        # Comment 2 is public, and not removed.
        self.assertEqual(cm2.id, 2)
        self.assertEqual(cm2.is_public, True)
        self.assertEqual(cm2.is_removed, False)
        # Comment 3 and 4 are not public, but not removed.
        for cm in [cm3, cm4]:
            self.assertEqual(cm.is_public, True)
            self.assertEqual(cm.is_removed, False)

        # Re-connect the function for the following tests.
        pre_save.connect(publish_or_withhold_on_pre_save,
                         sender=model_app_label)


class RenderLastXtdCommentsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.day_in_diary = Diary.objects.create(body="About Today...")

    def test_render_last_xtdcomments(self):
        # Send some nested comments to the article.
        thread_test_step_1(self.article)  # Sends 2 comments.
        thread_test_step_2(self.article)  # Sends 2 comments.
        thread_test_step_3(self.article)  # Sends 1 comment.
        # -> content:   cmt.id  thread_id  parent_id  level  order
        # cm1,   # ->      1         1          1        0      1
        # cm3,   # ->      3         1          1        1      2
        # cm4,   # ->      4         1          1        1      3
        # cm2,   # ->      2         2          2        0      1
        # cm5    # ->      5         2          2        1      2
        # And send another comment to the diary.
        add_comment_to_diary_entry(self.day_in_diary)

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

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MODEL=_xtd_model)
    def test_render_last_customized_comments(self):
        # Send nested comments using the MyComment model.
        thread_test_step_1(self.article, model=MyComment, title="title1")
        thread_test_step_2(self.article, model=MyComment, title="title2")
        thread_test_step_3(self.article, model=MyComment, title="title3")
        # Also send a comment of type MyComment to the diary.
        add_comment_to_diary_entry(self.day_in_diary, model=MyComment,
                                   title="title4")

        # render_last_xtdcomments should also render comments of the
        # model MyComment, defined in COMMENTS_XTD_MODEL setting.
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

    @patch.multiple('django_comments_xtd.conf.settings', SITE_ID=2)
    def test_render_last_xtdcomment_for_one_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')

        # Send some nested comments to the article in the site1.
        thread_test_step_1(self.article)  # Sends 2 comments.
        thread_test_step_2(self.article)  # Sends 2 comments.
        thread_test_step_3(self.article)  # Sends 1 comment.
        # And send another comment to the diary.
        add_comment_to_diary_entry(self.day_in_diary)  # Sends 1 comment.

        # Send some nested comments to the article in the site2.
        thread_test_step_1(self.article, site=site2)

        # render_last_xtdcomments should be able to list only the comments
        # posted to the active site.
        t = ("{% load comments_xtd %}"
             "{% render_last_xtdcomments 5 for tests.article tests.diary %}")
        output = Template(t).render(Context())

        # In  the output we will see only the comments sent to site2,
        # which have comment IDs 7 and 8.
        self.assertEqual(output.count('<a name='), 2)
        self.assertEqual(output.count('<a name="c8">'), 1)
        self.assertEqual(output.count('<a name="c7">'), 1)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_render_last_xtdcomments_for_HIDE_REMOVED_case_1(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # Previous two lines create the following comments:
        #  content ->    cmt.id  thread_id  parent_id  level  order
        #   cm1,   ->     1         1          1        0      1
        #   cm3,   ->     3         1          1        1      2
        #   cm4,   ->     4         1          1        1      3
        #   cm2,   ->     2         2          2        0      1
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing cm1, both cm3 and cm4 have is_public=False.
        # Therefore the list of comments should contain only cm2.
        t = ("{% load comments_xtd %}"
             "{% render_last_xtdcomments 5 for tests.article tests.diary %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<a name='), 1)
        self.assertEqual(output.count('<a name="c1">'), 0)
        self.assertEqual(output.count('<a name="c3">'), 0)
        self.assertEqual(output.count('<a name="c4">'), 0)
        self.assertEqual(output.count('<a name="c2">'), 1)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_render_last_xtdcomments_for_HIDE_REMOVED_case_2(self):
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
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        t = ("{% load comments_xtd %}"
             "{% render_last_xtdcomments 5 for tests.article tests.diary %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<a name='), 2)
        self.assertEqual(output.count('<a name="c1">'), 1)
        self.assertEqual(output.count('<a name="c3">'), 0)
        self.assertEqual(output.count('<a name="c4">'), 0)
        self.assertEqual(output.count('<a name="c2">'), 1)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False)
    def test_render_last_xtdcomments_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(publish_or_withhold_on_pre_save,
                            sender=model_app_label)
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()

        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()

        # After removing the cm1, both cm3 and cm4 remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        t = ("{% load comments_xtd %}"
             "{% render_last_xtdcomments 5 for tests.article tests.diary %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<a name='), 4)
        self.assertEqual(output.count('<a name="c1">'), 1)
        self.assertEqual(output.count('<a name="c3">'), 1)
        self.assertEqual(output.count('<a name="c4">'), 1)
        self.assertEqual(output.count('<a name="c2">'), 1)
        # Re-connect the function for the following tests.
        pre_save.connect(publish_or_withhold_on_pre_save,
                         sender=model_app_label)


class GetLastXtdCommentsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.day_in_diary = Diary.objects.create(body="About Today...")

    def test_get_last_xtdcomments(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        # -> content:   cmt.id  thread_id  parent_id  level  order
        # cm1,   # ->      1         1          1        0      1
        # cm3,   # ->      3         1          1        1      2
        # cm4,   # ->      4         1          1        1      3
        # cm2,   # ->      2         2          2        0      1
        # cm5    # ->      5         2          2        1      2
        # And send another comment to the diary.
        add_comment_to_diary_entry(self.day_in_diary)

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

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MODEL=_xtd_model)
    def test_get_last_customized_comments(self):
        # Send nested comments using the MyComment model.
        thread_test_step_1(self.article, model=MyComment, title="title1")
        thread_test_step_2(self.article, model=MyComment, title="title2")
        thread_test_step_3(self.article, model=MyComment, title="title3")
        # Also send a comment of type MyComment to the diary.
        add_comment_to_diary_entry(self.day_in_diary, model=MyComment,
                                   title="title4")
        # render_last_xtdcomments should also render comments of the
        # model MyComment, defined in COMMENTS_XTD_MODEL setting.
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

    @patch.multiple('django_comments_xtd.conf.settings', SITE_ID=2)
    def test_get_last_xtdcomment_for_one_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')

        # Send some nested comments to the article in the site1.
        thread_test_step_1(self.article)  # Sends 2 comments.
        thread_test_step_2(self.article)  # Sends 2 comments.
        thread_test_step_3(self.article)  # Sends 1 comment.
        # And send another comment to the diary.
        add_comment_to_diary_entry(self.day_in_diary)  # Sends 1 comment.

        # Send some nested comments to the article in the site2.
        thread_test_step_1(self.article, site=site2)

        # get_last_xtdcomments should be ablr to get only the comments
        # posted to the active site.
        t = ("{% load comments_xtd %}"
             "{% get_last_xtdcomments 5 as last_comments"
             "   for tests.article tests.diary %}"
             "{% for comment in last_comments %}"
             "<comment>{{ comment.id }}</comment>"
             "{% endfor %}")
        output = Template(t).render(Context())

        self.assertEqual(output.count('<comment>'), 2)
        self.assertEqual(output.count('<comment>8</comment>'), 1)
        self.assertEqual(output.count('<comment>7</comment>'), 1)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_last_xtdcomments_for_HIDE_REMOVED_case_1(self):
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # Previous two lines create the following comments:
        #  content ->    cmt.id  thread_id  parent_id  level  order
        #   cm1,   ->     1         1          1        0      1
        #   cm3,   ->     3         1          1        1      2
        #   cm4,   ->     4         1          1        1      3
        #   cm2,   ->     2         2          2        0      1
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # get_last_xtdcomments should get only cm2.
        t = ("{% load comments_xtd %}"
             "{% get_last_xtdcomments 5 as last_comments"
             "   for tests.article tests.diary %}"
             "{% for comment in last_comments %}"
             "<comment>{{ comment.id }}</comment>"
             "{% endfor %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<comment>'), 1)
        self.assertEqual(output.count('<comment>1</comment>'), 0)
        self.assertEqual(output.count('<comment>3</comment>'), 0)
        self.assertEqual(output.count('<comment>4</comment>'), 0)
        self.assertEqual(output.count('<comment>2</comment>'), 1)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_get_last_xtdcomments_for_HIDE_REMOVED_case_2(self):
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
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # After removing the cm1, both cm3 and cm4 have is_public=False,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is True. Therefore the
        # count should return 2 -> (cm1, cm2). cm1 is not hidden due to
        # COMMENTS_HIDE_REMOVED being False (a message will be displayed
        # saying that the comment has been removed, but the message won't be
        # removed from the queryset).
        t = ("{% load comments_xtd %}"
             "{% get_last_xtdcomments 5 as last_comments"
             "   for tests.article tests.diary %}"
             "{% for comment in last_comments %}"
             "<comment>{{ comment.id }}</comment>"
             "{% endfor %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<comment>'), 2)
        self.assertEqual(output.count('<comment>1</comment>'), 1)
        self.assertEqual(output.count('<comment>3</comment>'), 0)
        self.assertEqual(output.count('<comment>4</comment>'), 0)
        self.assertEqual(output.count('<comment>2</comment>'), 1)

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False)
    def test_render_last_xtdcomments_for_HIDE_REMOVED_case_3(self):
        model_app_label = get_model()._meta.label
        # The function publish_or_withhold_on_pre_save is only called if
        # COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED are True.
        pre_save.disconnect(publish_or_withhold_on_pre_save,
                            sender=model_app_label)
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        # These two lines create the following comments:
        # (  # content ->    cmt.id  thread_id  parent_id  level  order
        #     cm1,   # ->     1         1          1        0      1
        #     cm3,   # ->     3         1          1        1      2
        #     cm4,   # ->     4         1          1        1      3
        #     cm2,   # ->     2         2          2        0      1
        # ) = XtdComment.objects.all()

        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()

        # After removing the cm1, both cm3 and cm4 remain visible,
        # as COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED is False.
        t = ("{% load comments_xtd %}"
             "{% get_last_xtdcomments 5 as last_comments"
             "   for tests.article tests.diary %}"
             "{% for comment in last_comments %}"
             "<comment>{{ comment.id }}</comment>"
             "{% endfor %}")
        output = Template(t).render(Context())
        self.assertEqual(output.count('<comment>'), 4)
        self.assertEqual(output.count('<comment>1</comment>'), 1)
        self.assertEqual(output.count('<comment>3</comment>'), 1)
        self.assertEqual(output.count('<comment>4</comment>'), 1)
        self.assertEqual(output.count('<comment>2</comment>'), 1)

        # Re-connect the function for the following tests.
        pre_save.connect(publish_or_withhold_on_pre_save,
                         sender=model_app_label)


class XtdCommentsTreeTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.day_in_diary = Diary.objects.create(body="About Today...")

    def _create_comments(self, use_custom_model=False):
        kwargs = {}
        if use_custom_model:
            kwargs = { "model": MyComment, "title": "title1" }
        thread_test_step_1(self.article, **kwargs)
        thread_test_step_2(self.article, **kwargs)
        thread_test_step_3(self.article, **kwargs)
        thread_test_step_4(self.article, **kwargs)
        thread_test_step_5(self.article, **kwargs)

    def _assert_all_comments_are_published(self, use_custom_model=False):
        t = "{% load comments_xtd %}"
        if use_custom_model:  # Add the special template.
            t += ("{% render_xtdcomment_tree for object "
                  "using my_comments/comment_tree.html %}")
        else:
            t += "{% render_xtdcomment_tree for object %}"
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 9)
# testcase cmt.id   parent level-0  level-1  level-2
#  step1     1        -      c1                        <-                 cmt1
#  step2     3        1      --       c3               <-         cmt1 to cmt1
#  step5     8        3      --       --        c8     <- cmt1 to cmt1 to cmt1
#  step2     4        1      --       c4               <-         cmt2 to cmt1
#  step4     7        4      --       --        c7     <- cmt1 to cmt2 to cmt1
#  step1     2        -      c2                        <-                 cmt2
#  step3     5        2      --       c5               <-         cmt1 to cmt2
#  step4     6        5      --       --        c6     <- cmt1 to cmt1 to cmt2
#  step5     9        -      c9                        <-                 cmt9
        try:
            pos_c1 = output.index('<a name="c1"></a>')
            pos_c3 = output.index('<a name="c3"></a>')
            pos_c8 = output.index('<a name="c8"></a>')
            pos_c4 = output.index('<a name="c4"></a>')
            pos_c7 = output.index('<a name="c7"></a>')
            pos_c2 = output.index('<a name="c2"></a>')
            pos_c5 = output.index('<a name="c5"></a>')
            pos_c6 = output.index('<a name="c6"></a>')
            pos_c9 = output.index('<a name="c9"></a>')
        except ValueError as exc:
            self.fail(exc)
        else:
            self.assertTrue(pos_c1 < pos_c3 < pos_c8 <
                            pos_c4 < pos_c7 < pos_c2 <
                            pos_c5 < pos_c6 < pos_c9)

        if use_custom_model:
            # Check that the title field of the custom MyComment model
            # is also part of the output.
            try:
                title_c1 = output.index('<h5 id="title-1">')
                title_c3 = output.index('<h5 id="title-3">')
                title_c8 = output.index('<h5 id="title-8">')
                title_c4 = output.index('<h5 id="title-4">')
                title_c7 = output.index('<h5 id="title-7">')
                title_c2 = output.index('<h5 id="title-2">')
                title_c5 = output.index('<h5 id="title-5">')
                title_c6 = output.index('<h5 id="title-6">')
                title_c9 = output.index('<h5 id="title-9">')
            except ValueError as exc:
                self.fail(exc)
            else:
                self.assertTrue(title_c1 < title_c3 < title_c8 <
                                title_c4 < title_c7 < title_c2 <
                                title_c5 < title_c6 < title_c9)

    def test_render_xtdcomment_tree(self):
        self._create_comments()
        self._assert_all_comments_are_published()

    def _assert_only_comment_2_and_3_and_their_children_are_published(self):
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_tree for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 4)
        # Only the following comments must be displayed, the other ones must
        # have been withheld when setting the comment 1 is_public to False.
        pos_c2 = output.index('<a name="c2"></a>')
        pos_c5 = output.index('<a name="c5"></a>')
        pos_c6 = output.index('<a name="c6"></a>')
        pos_c9 = output.index('<a name="c9"></a>')
        self.assertTrue(pos_c2 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c9 > 0)
        self.assertTrue(pos_c2 < pos_c5 < pos_c6 < pos_c9)

    def test_withhold_comment_1(self):
        self._create_comments()
        # Now set comment 1 is_public to False.
        c1 = XtdComment.objects.get(pk=1)
        c1.is_public = False
        # Saving the instance triggers the pre_save signal in the models.py
        # module, which in turn withholds this comment and all its children.
        c1.save()
        self._assert_only_comment_2_and_3_and_their_children_are_published()

    def test_withhold_comment_1_and_publish_it_again(self):
        self._create_comments()
        # Now set comment 1 is_public to False.
        c1 = XtdComment.objects.get(pk=1)
        c1.is_public = False
        # Saving the instance triggers the pre_save signal in the models.py
        # module, which in turn withholds this comment and all its children.
        c1.save()
        self._assert_only_comment_2_and_3_and_their_children_are_published()

        c1.is_public = True
        # Saving the instance with is_public = True publish the comment and
        # all the nested comments.
        c1.save()
        self._assert_all_comments_are_published()

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MODEL=_xtd_model)
    def test_render_xtdcomment_tree_using_customized_comments(self):
        self._create_comments(use_custom_model=True)
        # Passsing use_custom_model will use the customized comments model,
        # and will check that the additional field provided with the
        # customized model is displayed in the tree of comments.
        self._assert_all_comments_are_published(use_custom_model=True)
        # Check that there are 9 instances of the custom model.
        self.assertEqual(MyComment.objects.count(), 9)

    @patch.multiple('django_comments_xtd.conf.settings', SITE_ID=2)
    def test_render_xtdcomment_tree_for_one_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')
        thread_test_step_1(self.article)
        thread_test_step_1(self.article, site=site2)
        thread_test_step_2(self.article, site=site2, parent_id=3)
        #           site    comment.id  parent.id
        #  step1      1          1          -
        #  step1      1          2          -
        #  step1      2          3          -
        #  step2      2          5          3
        #  step2      2          6          3
        #  step1      2          4          -
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_tree for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 4)
        # Only the following comments must be displayed, the other ones must
        # have been withheld when setting the comment 1 is_public to False.
        pos_c3 = output.index('<a name="c3"></a>')
        pos_c5 = output.index('<a name="c5"></a>')
        pos_c6 = output.index('<a name="c6"></a>')
        pos_c4 = output.index('<a name="c4"></a>')
        self.assertTrue(pos_c3 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c4 > 0)
        self.assertTrue(pos_c3 < pos_c5 < pos_c6 < pos_c4)

# ----------------------------------------------------------------------------
# testcase cmt.id   parent level-0  level-1  level-2
#  step1     2        -      c2                        <-                 cmt2
#  step3     5        2      --       c5               <-         cmt1 to cmt2
#  step4     6        5      --       --        c6     <- cmt1 to cmt1 to cmt2
#  step5     9        -      c9                        <-                 cmt9
    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_render_xtdcomment_tree_for_HIDE_REMOVED_case_1(self):
        self._create_comments()
        # As the comment over the method shows, when COMMENTS_HIDE_REMOVE is
        # True, removing the comment 1 removes the comment from the listing and
        # withholds all the nested comments too.
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        # Make changes in comments_xtd.py so that comments are removed from the
        # queryset when COMMENTS_HIDE_REMOVED is True.
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_tree for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 4)
        pos_c2 = output.index('<a name="c2"></a>')
        pos_c5 = output.index('<a name="c5"></a>')
        pos_c6 = output.index('<a name="c6"></a>')
        pos_c9 = output.index('<a name="c9"></a>')
        self.assertTrue(pos_c2 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c9 > 0)
        self.assertTrue(pos_c2 < pos_c5 < pos_c6 < pos_c9)

# ----------------------------------------------------------------------------
# testcase cmt.id   parent level-0  level-1  level-2
#  step1     1        -      c1                        <-                 cmt1
#  step1     2        -      c2                        <-                 cmt2
#  step3     5        2      --       c5               <-         cmt1 to cmt2
#  step4     6        5      --       --        c6     <- cmt1 to cmt1 to cmt2
#  step5     9        -      c9                        <-                 cmt9
    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_render_xtdcomment_tree_for_HIDE_REMOVED_case_2(self):
        self._create_comments()
        # As the comment above the method shows, when
        # XTD_COMMENTS_PUBLISH_OR_WITHHOLD_NESTED is True and
        # COMMENTS_HIDE_REMOVED is False, removing a comment make unvisible
        # its nested comments but keeps the removed one visible.
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_tree for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<a name='), 5)
        pos_c1 = output.index('<a name="c1"></a>')
        pos_c2 = output.index('<a name="c2"></a>')
        pos_c5 = output.index('<a name="c5"></a>')
        pos_c6 = output.index('<a name="c6"></a>')
        pos_c9 = output.index('<a name="c9"></a>')
        self.assertTrue(pos_c1 > 0)
        self.assertTrue(pos_c2 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c9 > 0)
        self.assertTrue(pos_c1 < pos_c2 < pos_c5 < pos_c6 < pos_c9)

# ----------------------------------------------------------------------------
# testcase cmt.id   parent level-0  level-1  level-2
#  step1     1        -      c1                        <-                 cmt1
#  step2     3        1      --       c3               <-         cmt1 to cmt1
#  step5     8        3      --       --        c8     <- cmt1 to cmt1 to cmt1
#  step2     4        1      --       c4               <-         cmt2 to cmt1
#  step4     7        4      --       --        c7     <- cmt1 to cmt2 to cmt1
#  step1     2        -      c2                        <-                 cmt2
#  step3     5        2      --       c5               <-         cmt1 to cmt2
#  step4     6        5      --       --        c6     <- cmt1 to cmt1 to cmt2
#  step5     9        -      c9                        <-                 cmt9
    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=False)
    def test_render_xtdcomment_tree_for_HIDE_REMOVED_case_3(self):
        self._create_comments()
        model_app_label = get_model()._meta.label
        pre_save.disconnect(publish_or_withhold_on_pre_save,
                            sender=model_app_label)
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        self._assert_all_comments_are_published()
        # Connect the receiver again.
        pre_save.connect(publish_or_withhold_on_pre_save,
                         sender=model_app_label)
