from io import StringIO
from django.core.management import call_command
from django.test import TestCase

from django_comments_xtd.models import XtdComment
from django_comments_xtd.tests.models import Article
from django_comments_xtd.tests.test_models import (
    thread_test_step_1, thread_test_step_2, thread_test_step_3,
    thread_test_step_4, thread_test_step_5
)


class InitializeNesteCoundCmdTest(TestCase):
    def setUp(self):
        self.article_1 = Article.objects.create(
            title="September", slug="september", body="During September...")
        thread_test_step_1(self.article_1)
        thread_test_step_2(self.article_1)
        thread_test_step_3(self.article_1)
        thread_test_step_4(self.article_1)
        thread_test_step_5(self.article_1)
        self.check_nested_count()

    def check_nested_count(self):
        (  # content ->    cmt.id  thread_id  parent_id  level  order  nested
            self.c1,  # ->   1         1          1        0      1      4
            self.c3,  # ->   3         1          1        1      2      1
            self.c8,  # ->   8         1          3        2      3      0
            self.c4,  # ->   4         1          1        1      4      1
            self.c7,  # ->   7         1          4        2      5      0
            self.c2,  # ->   2         2          2        0      1      2
            self.c5,  # ->   5         2          2        1      2      1
            self.c6,  # ->   6         2          5        2      3      0
            self.c9   # ->   9         9          9        0      1      0
        ) = XtdComment.objects.all()
        self.assertEqual(self.c1.nested_count, 4)
        self.assertEqual(self.c3.nested_count, 1)
        self.assertEqual(self.c8.nested_count, 0)
        self.assertEqual(self.c4.nested_count, 1)
        self.assertEqual(self.c7.nested_count, 0)
        self.assertEqual(self.c2.nested_count, 2)
        self.assertEqual(self.c5.nested_count, 1)
        self.assertEqual(self.c6.nested_count, 0)
        self.assertEqual(self.c9.nested_count, 0)

    def test_calling_command_computes_nested_count(self):
        # Set all comments nested_count field to 0.
        XtdComment.objects.update(nested_count=0)
        out = StringIO()
        call_command('initialize_nested_count', stdout=out)
        self.assertIn("Updated 9 XtdComment object(s).", out.getvalue())
        self.check_nested_count()

    def test_command_is_idempotent(self):
        out = StringIO()
        call_command('initialize_nested_count', stdout=out)
        call_command('initialize_nested_count', stdout=out)
        self.assertIn("Updated 9 XtdComment object(s).", out.getvalue())
        self.check_nested_count()
