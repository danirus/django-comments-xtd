from unittest.mock import patch

from django.db.models.signals import pre_save
from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.template import Context, Template
from django.test import TestCase as DjangoTestCase

from django_comments_xtd import get_model
from django_comments_xtd.models import (XtdComment,
                                        publish_or_withhold_on_pre_save)
from django_comments_xtd.utils import get_current_site_id

from django_comments_xtd.tests.models import Article, MyComment
from django_comments_xtd.tests.test_models import (
    thread_test_step_1, thread_test_step_2, thread_test_step_3,
    thread_test_step_4, thread_test_step_5)


_xtd_model = "django_comments_xtd.tests.models.MyComment"


class RenderXtdCommentListTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")

    def _create_comments(self, use_custom_model=False):
        #  step   id   parent level-0  level-1  level-2
        #    1     1      -      c1                     <- cm1
        #    2     3      1      --       c3            <-  cm1 to cm1
        #    5     8      3      --       --       c8   <-   cm1 to cm1 to cm1
        #    2     4      1      --       c4            <-  cm2 to cm1
        #    4     7      4      --       --       c7   <-   cm1 to cm2 to cm1
        #    1     2      -      c2                     <- cm2
        #    3     5      2      --       c5            <-  cm1 to cm2
        #    4     6      5      --       --       c6   <-   cm1 to cm1 to cm2
        #    5     9      -      c9                     <- cm9
        kwargs = {}
        if use_custom_model:
            kwargs = {"model": MyComment, "title": "title1"}
        thread_test_step_1(self.article, **kwargs)
        thread_test_step_2(self.article, **kwargs)
        thread_test_step_3(self.article, **kwargs)
        thread_test_step_4(self.article, **kwargs)
        thread_test_step_5(self.article, **kwargs)

    def _assert_all_comments_are_published(self, use_custom_model=False):
        t = "{% load comments comments_xtd %}"
        if use_custom_model:
            t += ("{% render_xtdcomment_list for object "
                  "using my_comments/list.html %}")
        else:
            t += "{% render_xtdcomment_list for object %}"
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<div id="c'), 9)
        try:
            pos_c1 = output.index('<div id="c1"')
            pos_c3 = output.index('<div id="c3"')
            pos_c8 = output.index('<div id="c8"')
            pos_c4 = output.index('<div id="c4"')
            pos_c7 = output.index('<div id="c7"')
            pos_c2 = output.index('<div id="c2"')
            pos_c5 = output.index('<div id="c5"')
            pos_c6 = output.index('<div id="c6"')
            pos_c9 = output.index('<div id="c9"')
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


    def test_render_xtdcomment_list(self):
        self._create_comments()
        self._assert_all_comments_are_published()

    def _assert_only_comment_2_and_3_and_their_children_are_published(self):
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_list for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<div id="c'), 4)
        # Only the following comments must be displayed, the other ones must
        # have been withheld when setting the comment 1 is_public to False.
        pos_c2 = output.index('<div id="c2"')
        pos_c5 = output.index('<div id="c5"')
        pos_c6 = output.index('<div id="c6"')
        pos_c9 = output.index('<div id="c9"')
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

    @patch.multiple('django.conf.settings', SITE_ID=2)
    def test_render_xtdcomment_list_for_one_site(self):
        site2 = Site.objects.create(domain='site2.com', name='site2.com')
        self.assertEqual(get_current_site_id(), 2)
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
             "{% render_xtdcomment_list for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<div id='), 4)
        # Only the following comments must be displayed, the other ones must
        # have been withheld when setting the comment 1 is_public to False.
        pos_c3 = output.index('<div id="c3"')
        pos_c5 = output.index('<div id="c5"')
        pos_c6 = output.index('<div id="c6"')
        pos_c4 = output.index('<div id="c4"')
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
    @patch.multiple('django.conf.settings',
                    COMMENTS_HIDE_REMOVED=True,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_render_xtdcomment_list_for_HIDE_REMOVED_case_1(self):
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
             "{% render_xtdcomment_list for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<div id='), 4)
        pos_c2 = output.index('<div id="c2"')
        pos_c5 = output.index('<div id="c5"')
        pos_c6 = output.index('<div id="c6"')
        pos_c9 = output.index('<div id="c9"')
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
    @patch.multiple('django.conf.settings',
                    COMMENTS_HIDE_REMOVED=False,
                    COMMENTS_XTD_PUBLISH_OR_WITHHOLD_NESTED=True)
    def test_render_xtdcomment_list_for_HIDE_REMOVED_case_2(self):
        self._create_comments()
        # As the comment above the method shows, when
        # XTD_COMMENTS_PUBLISH_OR_WITHHOLD_NESTED is True and
        # COMMENTS_HIDE_REMOVED is False, removing a comment make unvisible
        # its nested comments but keeps the removed one visible.
        cm1 = XtdComment.objects.get(pk=1)
        cm1.is_removed = True
        cm1.save()
        t = ("{% load comments_xtd %}"
             "{% render_xtdcomment_list for object %}")
        output = Template(t).render(Context({'object': self.article,
                                             'user': AnonymousUser()}))
        self.assertEqual(output.count('<div id="c'), 5)
        pos_c1 = output.index('<div id="c1"')
        pos_c2 = output.index('<div id="c2"')
        pos_c5 = output.index('<div id="c5"')
        pos_c6 = output.index('<div id="c6"')
        pos_c9 = output.index('<div id="c9"')
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
    @patch.multiple('django.conf.settings',
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




class CommentCSSThreadRangeTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September...")

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

        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        thread_test_step_4(self.article)
        thread_test_step_5(self.article)

    def test_tag_with_comments_of_level_1(self):
        for pk in [1, 2, 9]:
            cm = XtdComment.objects.get(pk=pk)
            self.assertEqual(cm.level, 0)
            t = ("{% load comments_xtd %}"
                "{% comment_css_thread_range object %}")
            output = Template(t).render(Context({'object': cm}))
            self.assertEqual(output, "l0-ini")

    def test_tag_with_comment_of_level_2(self):
        for pk in [3, 4, 5]:
            cm = XtdComment.objects.get(pk=pk)
            self.assertEqual(cm.level, 1)
            t = ("{% load comments_xtd %}"
                "{% comment_css_thread_range object %}")
            output = Template(t).render(Context({'object': cm}))
            self.assertEqual(output, "l0-mid l1-ini")

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MAX_THREAD_LEVEL=2)
    def test_tag_with_comment_of_level_3_eq_max_thread_level(self):
        for pk in [6, 7, 8]:
            cm = XtdComment.objects.get(pk=pk)
            self.assertEqual(cm.level, 2)
            t = ("{% load comments_xtd %}"
                "{% comment_css_thread_range object %}")
            output = Template(t).render(Context({'object': cm}))
            self.assertEqual(output, "l0-mid l1-mid l2")

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MAX_THREAD_LEVEL=2)
    def test_tag_with_comment_of_level_3_eq_max_thread_level_and_prefix(self):
        for pk in [6, 7, 8]:
            cm = XtdComment.objects.get(pk=pk)
            self.assertEqual(cm.level, 2)
            t = ("{% load comments_xtd %}"
                "{% comment_css_thread_range object 'thread-' %}")
            output = Template(t).render(Context({'object': cm}))
            self.assertEqual(output, "thread-0-mid thread-1-mid thread-2")
