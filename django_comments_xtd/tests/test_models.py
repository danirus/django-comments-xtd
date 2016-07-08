from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase as DjangoTestCase

from django_comments_xtd.models import (XtdComment,
                                        MaxThreadLevelExceededException)
from django_comments_xtd.tests.models import Article, Diary


class ArticleBaseTestCase(DjangoTestCase):
    def setUp(self):
        self.article_1 = Article.objects.create(
            title="September", slug="september", body="During September...")
        self.article_2 = Article.objects.create(
            title="October", slug="october", body="What I did on October...")


class XtdCommentManagerTestCase(ArticleBaseTestCase):
    def test_for_app_models(self):
        # there is no comment posted yet to article_1 nor article_2
        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 0)

        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site = Site.objects.get(pk=1)

        # post one comment to article_1
        XtdComment.objects.create(content_type=article_ct,
                                  object_pk=self.article_1.id,
                                  content_object=self.article_1,
                                  site=site,
                                  comment="just a testing comment",
                                  submit_date=datetime.now())

        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 1)

        # post one comment to article_2
        XtdComment.objects.create(content_type=article_ct,
                                  object_pk=self.article_2.id,
                                  content_object=self.article_2,
                                  site=site,
                                  comment="yet another comment",
                                  submit_date=datetime.now())

        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 2)

        # post a second comment to article_2
        XtdComment.objects.create(content_type=article_ct,
                                  object_pk=self.article_2.id,
                                  content_object=self.article_2,
                                  site=site,
                                  comment="and another one",
                                  submit_date=datetime.now())

        count = XtdComment.objects.for_app_models("tests.article").count()
        self.assert_(count == 3)

# In order to methods save and test _calculate_thread_ata, simulate the
# following threads, in order of arrival:
#
# testcase cmt.id   parent level-0  level-1  level-2
#  step1     1        -      c1                        <-                 cmt1
#  step1     2        -      c2                        <-                 cmt2
#  step2     3        1      --       c3               <-         cmt1 to cmt1
#  step2     4        1      --       c4               <-         cmt2 to cmt1
#  step3     5        2      --       c5               <-         cmt1 to cmt2
#  step4     6        5      --       --        c6     <- cmt1 to cmt1 to cmt2
#  step4     7        4      --       --        c7     <- cmt1 to cmt2 to cmt1
#  step5     8        3      --       --        c8     <- cmt1 to cmt1 to cmt1
#  step5     9        -      c9                        <-                 cmt9


def thread_test_step_1(article):
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)

    # post Comment 1 with parent_id 0
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="comment 1 to article",
                              submit_date=datetime.now())

    # post Comment 2 with parent_id 0
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="comment 2 to article",
                              submit_date=datetime.now())


def thread_test_step_2(article):
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)

    # post Comment 3 to parent_id 1
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="comment 1 to comment 1",
                              submit_date=datetime.now(),
                              parent_id=1)

    # post Comment 4 to parent_id 1
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="comment 2 to comment 1",
                              submit_date=datetime.now(),
                              parent_id=1)


def thread_test_step_3(article):
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)

    # post Comment 5 to parent_id 2
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="comment 1 to comment 1",
                              submit_date=datetime.now(),
                              parent_id=2)


def thread_test_step_4(article):
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)

    # post Comment 6 to parent_id 5
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="cmt 1 to cmt 1 to cmt 2",
                              submit_date=datetime.now(),
                              parent_id=5)

    # post Comment 7 to parent_id 4
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="cmt 1 to cmt 2 to cmt 1",
                              submit_date=datetime.now(),
                              parent_id=4)


def thread_test_step_5(article):
    article_ct = ContentType.objects.get(app_label="tests", model="article")
    site = Site.objects.get(pk=1)

    # post Comment 8 to parent_id 3
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="cmt 1 to cmt 1 to cmt 1",
                              submit_date=datetime.now(),
                              parent_id=3)

    # post Comment 9 with parent_id 0
    XtdComment.objects.create(content_type=article_ct,
                              object_pk=article.id,
                              content_object=article,
                              site=site,
                              comment="cmt 1 to cmt 2 to cmt 1",
                              submit_date=datetime.now())


class BaseThreadStep1TestCase(ArticleBaseTestCase):
    def setUp(self):
        super(BaseThreadStep1TestCase, self).setUp()
        thread_test_step_1(self.article_1)
        (  # content ->     cmt.id  thread_id  parent_id  level  order
            self.c1,  # ->    1         1          1        0      1
            self.c2   # ->    2         2          2        0      1
        ) = XtdComment.objects.all()

    def test_threaded_comments_step_1_level_0(self):
        # comment 1
        self.assert_(self.c1.parent_id == 1 and self.c1.thread_id == 1)
        self.assert_(self.c1.level == 0 and self.c1.order == 1)
        # comment 2
        self.assert_(self.c2.parent_id == 2 and self.c2.thread_id == 2)
        self.assert_(self.c2.level == 0 and self.c2.order == 1)


class ThreadStep2TestCase(ArticleBaseTestCase):
    def setUp(self):
        super(ThreadStep2TestCase, self).setUp()
        thread_test_step_1(self.article_1)
        thread_test_step_2(self.article_1)
        (  # content ->    cmt.id  thread_id  parent_id  level  order
            self.c1,  # ->   1         1          1        0      1
            self.c3,  # ->   3         1          1        1      2
            self.c4,  # ->   4         1          1        1      3
            self.c2   # ->   2         2          2        0      1
        ) = XtdComment.objects.all()

    def test_threaded_comments_step_2_level_0(self):
        # comment 1
        self.assert_(self.c1.parent_id == 1 and self.c1.thread_id == 1)
        self.assert_(self.c1.level == 0 and self.c1.order == 1)
        # comment 2
        self.assert_(self.c2.parent_id == 2 and self.c2.thread_id == 2)
        self.assert_(self.c2.level == 0 and self.c2.order == 1)

    def test_threaded_comments_step_2_level_1(self):
        # comment 3
        self.assert_(self.c3.parent_id == 1 and self.c3.thread_id == 1)
        self.assert_(self.c3.level == 1 and self.c3.order == 2)
        # comment 4
        self.assert_(self.c4.parent_id == 1 and self.c4.thread_id == 1)
        self.assert_(self.c4.level == 1 and self.c4.order == 3)


class ThreadStep3TestCase(ArticleBaseTestCase):
    def setUp(self):
        super(ThreadStep3TestCase, self).setUp()
        thread_test_step_1(self.article_1)
        thread_test_step_2(self.article_1)
        thread_test_step_3(self.article_1)

        (  # -> content:   cmt.id  thread_id  parent_id  level  order
            self.c1,  # ->   1         1          1        0      1
            self.c3,  # ->   3         1          1        1      2
            self.c4,  # ->   4         1          1        1      3
            self.c2,  # ->   2         2          2        0      1
            self.c5   # ->   5         2          2        1      2
        ) = XtdComment.objects.all()

    def test_threaded_comments_step_3_level_0(self):
        # comment 1
        self.assert_(self.c1.parent_id == 1 and self.c1.thread_id == 1)
        self.assert_(self.c1.level == 0 and self.c1.order == 1)
        # comment 2
        self.assert_(self.c2.parent_id == 2 and self.c2.thread_id == 2)
        self.assert_(self.c2.level == 0 and self.c2.order == 1)

    def test_threaded_comments_step_3_level_1(self):
        # comment 3
        self.assert_(self.c3.parent_id == 1 and self.c3.thread_id == 1)
        self.assert_(self.c3.level == 1 and self.c3.order == 2)
        # comment 4
        self.assert_(self.c4.parent_id == 1 and self.c4.thread_id == 1)
        self.assert_(self.c4.level == 1 and self.c4.order == 3)
        # comment 5
        self.assert_(self.c5.parent_id == 2 and self.c5.thread_id == 2)
        self.assert_(self.c5.level == 1 and self.c5.order == 2)


class ThreadStep4TestCase(ArticleBaseTestCase):
    def setUp(self):
        super(ThreadStep4TestCase, self).setUp()
        thread_test_step_1(self.article_1)
        thread_test_step_2(self.article_1)
        thread_test_step_3(self.article_1)
        thread_test_step_4(self.article_1)

        (  # content ->    cmt.id  thread_id  parent_id  level  order
            self.c1,  # ->   1         1          1        0      1
            self.c3,  # ->   3         1          1        1      2
            self.c4,  # ->   4         1          1        1      3
            self.c7,  # ->   7         1          4        2      4
            self.c2,  # ->   2         2          2        0      1
            self.c5,  # ->   5         2          2        1      2
            self.c6   # ->   6         2          5        2      3
        ) = XtdComment.objects.all()

    def test_threaded_comments_step_4_level_0(self):
        # comment 1
        self.assert_(self.c1.parent_id == 1 and self.c1.thread_id == 1)
        self.assert_(self.c1.level == 0 and self.c1.order == 1)
        # comment 2
        self.assert_(self.c2.parent_id == 2 and self.c2.thread_id == 2)
        self.assert_(self.c2.level == 0 and self.c2.order == 1)

    def test_threaded_comments_step_4_level_1(self):
        # comment 3
        self.assert_(self.c3.parent_id == 1 and self.c3.thread_id == 1)
        self.assert_(self.c3.level == 1 and self.c3.order == 2)
        # comment 4
        self.assert_(self.c4.parent_id == 1 and self.c4.thread_id == 1)
        self.assert_(self.c4.level == 1 and self.c4.order == 3)
        # comment 5
        self.assert_(self.c5.parent_id == 2 and self.c5.thread_id == 2)
        self.assert_(self.c5.level == 1 and self.c5.order == 2)

    def test_threaded_comments_step_4_level_2(self):
        # comment 6
        self.assert_(self.c6.parent_id == 5 and self.c6.thread_id == 2)
        self.assert_(self.c6.level == 2 and self.c6.order == 3)
        # comment 7
        self.assert_(self.c7.parent_id == 4 and self.c7.thread_id == 1)
        self.assert_(self.c7.level == 2 and self.c7.order == 4)


class ThreadStep5TestCase(ArticleBaseTestCase):
    def setUp(self):
        super(ThreadStep5TestCase, self).setUp()
        thread_test_step_1(self.article_1)
        thread_test_step_2(self.article_1)
        thread_test_step_3(self.article_1)
        thread_test_step_4(self.article_1)
        thread_test_step_5(self.article_1)

        (  # content ->    cmt.id  thread_id  parent_id  level  order
            self.c1,  # ->   1         1          1        0      1
            self.c3,  # ->   3         1          1        1      2
            self.c8,  # ->   8         1          3        2      3
            self.c4,  # ->   4         1          1        1      4
            self.c7,  # ->   7         1          4        2      5
            self.c2,  # ->   2         2          2        0      1
            self.c5,  # ->   5         2          2        1      2
            self.c6,  # ->   6         2          5        2      3
            self.c9   # ->   9         9          9        0      1
        ) = XtdComment.objects.all()

    def test_threaded_comments_step_5_level_0(self):
        # comment 1
        self.assert_(self.c1.parent_id == 1 and self.c1.thread_id == 1)
        self.assert_(self.c1.level == 0 and self.c1.order == 1)
        # comment 2
        self.assert_(self.c2.parent_id == 2 and self.c2.thread_id == 2)
        self.assert_(self.c2.level == 0 and self.c2.order == 1)
        # comment 9
        self.assert_(self.c9.parent_id == 9 and self.c9.thread_id == 9)
        self.assert_(self.c9.level == 0 and self.c9.order == 1)

    def test_threaded_comments_step_5_level_1(self):
        # comment 3
        self.assert_(self.c3.parent_id == 1 and self.c3.thread_id == 1)
        self.assert_(self.c3.level == 1 and self.c3.order == 2)
        # comment 4
        self.assert_(self.c4.parent_id == 1 and self.c4.thread_id == 1)
        self.assert_(self.c4.level == 1 and self.c4.order == 4)  # changed
        # comment 5
        self.assert_(self.c5.parent_id == 2 and self.c5.thread_id == 2)
        self.assert_(self.c5.level == 1 and self.c5.order == 2)

    def test_threaded_comments_step_5_level_2(self):
        # comment 6
        self.assert_(self.c6.parent_id == 5 and self.c6.thread_id == 2)
        self.assert_(self.c6.level == 2 and self.c6.order == 3)
        # comment 7
        self.assert_(self.c7.parent_id == 4 and self.c7.thread_id == 1)
        self.assert_(self.c7.level == 2 and self.c7.order == 5)  # changed
        # comment 8
        self.assert_(self.c8.parent_id == 3 and self.c8.thread_id == 1)
        self.assert_(self.c8.level == 2 and self.c8.order == 3)

    def test_exceed_max_thread_level_raises_exception(self):
        article_ct = ContentType.objects.get(app_label="tests", model="article")
        site = Site.objects.get(pk=1)
        with self.assertRaises(MaxThreadLevelExceededException):
            XtdComment.objects.create(content_type=article_ct,
                                      object_pk=self.article_1.id,
                                      content_object=self.article_1,
                                      site=site,
                                      comment="cmt 1 to cmt 2 to cmt 1",
                                      submit_date=datetime.now(),
                                      parent_id=8)  # already max thread level


class DiaryBaseTestCase(DjangoTestCase):
    def setUp(self):
        self.day_in_diary = Diary.objects.create(body="About Today...")
        diary_ct = ContentType.objects.get(app_label="tests", model="diary")
        site = Site.objects.get(pk=1)
        XtdComment.objects.create(content_type=diary_ct,
                                  object_pk=self.day_in_diary.id,
                                  content_object=self.day_in_diary,
                                  site=site,
                                  comment="cmt to day in diary",
                                  submit_date=datetime.now())

    def test_max_thread_level_by_app_model(self):
        diary_ct = ContentType.objects.get(app_label="tests", model="diary")
        site = Site.objects.get(pk=1)
        with self.assertRaises(MaxThreadLevelExceededException):
            XtdComment.objects.create(content_type=diary_ct,
                                      object_pk=self.day_in_diary.id,
                                      content_object=self.day_in_diary,
                                      site=site,
                                      comment="cmt to cmt to day in diary",
                                      submit_date=datetime.now(),
                                      parent_id=1)  # already max thread level
