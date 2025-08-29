from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template
from django.test import TestCase as DjangoTestCase

from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article, Diary
from django_comments_xtd.tests.test_models import (
    add_comment_to_diary_entry,
    thread_test_step_1,
    thread_test_step_2,
    thread_test_step_3,
    thread_test_step_4,
    thread_test_step_5,
    thread_test_step_6,
)


class GetXtdCommentCountTestCase(DjangoTestCase):
    def setUp(self):
        self.article_1 = Article.objects.create(
            title="September", slug="september", body="During September..."
        )
        self.article_2 = Article.objects.create(
            title="October", slug="october", body="What I did on October..."
        )
        self.day_in_diary = Diary.objects.create(body="About Today...")

    def test_get_xtdcomment_count_for_one_model(self):
        thread_test_step_1(self.article_1)
        t = (
            "{% load comments_xtd %}"
            "{% get_xtdcomment_count as varname for tests.article %}"
            "{{ varname }}"
        )
        self.assertEqual(Template(t).render(Context()), "2")

    def test_get_xtdcomment_count_for_two_models(self):
        thread_test_step_1(self.article_1)
        add_comment_to_diary_entry(self.day_in_diary)
        t = (
            "{% load comments_xtd %}"
            "{% get_xtdcomment_count as varname"
            "   for tests.article tests.diary %}"
            "{{ varname }}"
        )
        self.assertEqual(Template(t).render(Context()), "3")


class LastXtdCommentsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September..."
        )
        self.day_in_diary = Diary.objects.create(body="About Today...")
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        add_comment_to_diary_entry(self.day_in_diary)

    def test_render_last_xtdcomments(self):
        t = (
            "{% load comments_xtd %}"
            "{% render_last_xtdcomments 5 for tests.article tests.diary %}"
        )
        output = Template(t).render(Context())
        self.assertEqual(output.count("<a id="), 5)
        self.assertEqual(output.count('<a id="c6">'), 1)
        self.assertEqual(output.count('<a id="c5">'), 1)
        self.assertEqual(output.count('<a id="c4">'), 1)
        self.assertEqual(output.count('<a id="c3">'), 1)
        self.assertEqual(output.count('<a id="c2">'), 1)
        # We added 6 comments, and we render the last 5, so
        # the first one must not be rendered in the output.
        self.assertEqual(output.count('<a id="c1">'), 0)

    def test_get_last_xtdcomments(self):
        t = (
            "{% load comments_xtd %}"
            "{% get_last_xtdcomments 5 as last_comments"
            "   for tests.article tests.diary %}"
            "{% for comment in last_comments %}"
            "<comment>{{ comment.id }}</comment>"
            "{% endfor %}"
        )
        output = Template(t).render(Context())
        self.assertEqual(output.count("<comment>"), 5)
        self.assertEqual(output.count("<comment>6</comment>"), 1)
        self.assertEqual(output.count("<comment>5</comment>"), 1)
        self.assertEqual(output.count("<comment>4</comment>"), 1)
        self.assertEqual(output.count("<comment>3</comment>"), 1)
        self.assertEqual(output.count("<comment>2</comment>"), 1)
        # We added 6 comments, and we render the last 5, so
        # the first one must not be rendered in the output.
        self.assertEqual(output.count("<comment>1</comment>"), 0)


class XtdCommentsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September..."
        )
        self.day_in_diary = Diary.objects.create(body="About Today...")
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        thread_test_step_4(self.article)
        thread_test_step_5(self.article)

    def _assert_all_comments_are_published(self):
        t = "{% load comments_xtd %}{% render_xtdcomment_tree for object %}"
        output = Template(t).render(
            Context({"object": self.article, "user": AnonymousUser()})
        )
        self.assertEqual(output.count('<div id="c'), 9)
        # See test_models.py, ThreadStep5TestCase to get a quick
        # view of the comments posted and their thread structure.
        pos_c1 = output.index('<div id="c1"')
        pos_c3 = output.index('<div id="c3"')
        pos_c8 = output.index('<div id="c8"')
        pos_c4 = output.index('<div id="c4"')
        pos_c7 = output.index('<div id="c7"')
        pos_c2 = output.index('<div id="c2"')
        pos_c5 = output.index('<div id="c5"')
        pos_c6 = output.index('<div id="c6"')
        pos_c9 = output.index('<div id="c9"')
        self.assertTrue(pos_c1 > 0)
        self.assertTrue(pos_c3 > 0)
        self.assertTrue(pos_c8 > 0)
        self.assertTrue(pos_c4 > 0)
        self.assertTrue(pos_c7 > 0)
        self.assertTrue(pos_c2 > 0)
        self.assertTrue(pos_c5 > 0)
        self.assertTrue(pos_c6 > 0)
        self.assertTrue(pos_c9 > 0)
        self.assertTrue(
            pos_c1
            < pos_c3
            < pos_c8
            < pos_c4
            < pos_c7
            < pos_c2
            < pos_c5
            < pos_c6
            < pos_c9
        )

    def test_render_xtdcomment_tree(self):
        self._assert_all_comments_are_published()

    def _assert_only_comment_2_and_3_and_their_children_are_published(self):
        t = "{% load comments_xtd %}{% render_xtdcomment_tree for object %}"
        output = Template(t).render(
            Context({"object": self.article, "user": AnonymousUser()})
        )
        self.assertEqual(output.count('<div id="c'), 4)
        # Only the following comments must be displayed, the other ones must
        # have been unpublished when setting the comment 1 is_public to False.
        pos_c2 = output.index('<div id="c2"')
        pos_c5 = output.index('<div id="c5"')
        pos_c6 = output.index('<div id="c6"')
        pos_c9 = output.index('<div id="c9"')
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


class RenderCommentThreadsTestCase(DjangoTestCase):
    def setUp(self):
        self.article = Article.objects.create(
            title="September", slug="september", body="During September..."
        )
        thread_test_step_1(self.article)
        thread_test_step_2(self.article)
        thread_test_step_3(self.article)
        thread_test_step_4(self.article)
        thread_test_step_5(self.article)
        thread_test_step_6(self.article)
        #
        # The previous 5 calls create the following comments:
        #
        # step  cmt.id   parent lv-0  lv-1  lv-2  lv-3
        #  1      1        -     c1                      c1
        #  2      3        1     --    c3                c1 <- c3
        #  5      8        3     --    --    c8          c1 <- c3 <- c8
        #  6     11        8     --    --    --   c11    c1 <- c3 <- c8 <- c11
        #  2      4        1     --    c4                c1 <- c4
        #  4      7        4     --    --    c7          c1 <- c4 <- c7
        #  6     10        7     --    --    --   c10    c1 <- c4 <- c7 <- c10
        #  1      2        -     c2                      c2
        #  3      5        2     --    c5                c2 <- c5
        #  4      6        5     --    --    c6          c2 <- c5 <- c6
        #  5      9        -     c9                      c9

    def render_template_tag(self, comment, reply_stack_ids):
        # Create the reply_stack with actual comments, as
        # it is in the context of the list.html template:
        reply_stack = [XtdComment.objects.get(pk=pk) for pk in reply_stack_ids]
        t = (
            "{% load comments_xtd %}"
            "{% render_comment_threads for object %}"
        )
        context = Context({
            "object": comment,
            "reply_stack": reply_stack
        })
        return Template(t).render(context)

    def test_tag_for_comment_1__of_level_0(self):
        cm = XtdComment.objects.get(pk=1)
        self.assertEqual(cm.level, 0)
        reply_stack = [1]  # IDs in the reply_stack when rendering cm 1.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0 cthread-ini"'
            ' data-djcx-cthread-id="1"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_3__of_level_1(self):
        cm = XtdComment.objects.get(pk=3)
        self.assertEqual(cm.level, 1)
        reply_stack = [1, 3]  # IDs in the reply_stack when rendering cm 3.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="1"></a>'
            '<a class="cthread cthread-l1 cthread-ini"'
            ' data-djcx-cthread-id="3"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_8__of_level_2(self):
        cm = XtdComment.objects.get(pk=8)
        self.assertEqual(cm.level, 2)
        reply_stack = [1, 3, 8]  # IDs in reply_stack when rendering cm 8.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="1"></a>'
            '<a class="cthread cthread-l1" data-djcx-cthread-id="3"></a>'
            '<a class="cthread cthread-l2 cthread-ini"'
            ' data-djcx-cthread-id="8"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_11__of_level_3(self):
        cm = XtdComment.objects.get(pk=11)
        self.assertEqual(cm.level, 3)
        reply_stack = [1, 3, 8, 11]  # IDs in reply_stack when rendering cm 11.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="1"></a>'
            '<a class="cthread cthread-l1" data-djcx-cthread-id="3"></a>'
            '<a class="cthread cthread-l2" data-djcx-cthread-id="8"></a>'
            '<span class="cthread-end"></span>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_4__of_level_1(self):
        cm = XtdComment.objects.get(pk=4)
        self.assertEqual(cm.level, 1)
        reply_stack = [1, 4]  # IDs in the reply_stack when rendering cm 4.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="1"></a>'
            '<a class="cthread cthread-l1 cthread-ini"'
            ' data-djcx-cthread-id="4"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_7__of_level_2(self):
        cm = XtdComment.objects.get(pk=7)
        self.assertEqual(cm.level, 2)
        reply_stack = [1, 4, 7]  # IDs in reply_stack when rendering cm 7.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="1"></a>'
            '<a class="cthread cthread-l1" data-djcx-cthread-id="4"></a>'
            '<a class="cthread cthread-l2 cthread-ini"'
            ' data-djcx-cthread-id="7"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_10__of_level_3(self):
        cm = XtdComment.objects.get(pk=10)
        self.assertEqual(cm.level, 3)
        reply_stack = [1, 4, 7, 10]  # IDs in reply_stack when rendering cm 10.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="1"></a>'
            '<a class="cthread cthread-l1" data-djcx-cthread-id="4"></a>'
            '<a class="cthread cthread-l2" data-djcx-cthread-id="7"></a>'
            '<span class="cthread-end"></span>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_2__of_level_0(self):
        cm = XtdComment.objects.get(pk=2)
        self.assertEqual(cm.level, 0)
        reply_stack = [2]  # IDs in the reply_stack when rendering cm 2.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0 cthread-ini"'
            ' data-djcx-cthread-id="2"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_5__of_level_1(self):
        cm = XtdComment.objects.get(pk=5)
        self.assertEqual(cm.level, 1)
        reply_stack = [2, 5]  # IDs in the reply_stack when rendering cm 5.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="2"></a>'
            '<a class="cthread cthread-l1 cthread-ini"'
            ' data-djcx-cthread-id="5"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_6__of_level_2(self):
        cm = XtdComment.objects.get(pk=6)
        self.assertEqual(cm.level, 2)
        reply_stack = [2, 5, 6]  # IDs in reply_stack when rendering cm 6.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0" data-djcx-cthread-id="2"></a>'
            '<a class="cthread cthread-l1" data-djcx-cthread-id="5"></a>'
            '<a class="cthread cthread-l2 cthread-ini"'
            ' data-djcx-cthread-id="6"></a>'
        )
        self.assertEqual(output, expected)

    def test_tag_for_comment_9__of_level_0(self):
        cm = XtdComment.objects.get(pk=9)
        self.assertEqual(cm.level, 0)
        reply_stack = [9]  # IDs in the reply_stack when rendering cm 9.
        output = self.render_template_tag(cm, reply_stack)
        expected = (
            '<a class="cthread cthread-l0 cthread-ini"'
            ' data-djcx-cthread-id="9"></a>'
        )
        self.assertEqual(output, expected)



class RenderCommentThreadsInReplyBoxTestCase(DjangoTestCase):
    pass

# This table represents the comment tree with the values of the variables
# `comment` and `reply_stack` in the template context at the time the
# template `comments/reply_button.html` is included in the `list.html`
# to be rendered.
#
# Max thread level in this example is 2.
#
# cmt.id   parent l-0  l-1  l-2  |    context:    comment      reply_stack
#   20       -     c1            |                             c20
#   33      20     --  c33       |                             c20 <- c33
#                                reply for c33:
#                                reply for c20:
#   21       -    c21            |                             c21
#                                reply for c21:
#   22       -    c22            |                             c22
#   42      22     --  c42       |                             c22 <- c42
#                                reply for c42:
#   48      22     --  c48       |                             c22 <- c48
#   52      48     --   --  c52  |                             c22 <- c48
#   56      48     --   --  c56  |                             c22 <- c48
#                                reply for c48:   c48          c22
#                                reply for c22:
