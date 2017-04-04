try:
    from unittest.mock import patch
except ImportError:
    from mock import patch
import unittest

from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase as DjangoTestCase

from django_comments_xtd.templatetags.comments_xtd import (
    render_markup_comment, formatter)

from django_comments_xtd.tests.models import Article, Diary
from django_comments_xtd.tests.test_models import (
    thread_test_step_1, thread_test_step_2, thread_test_step_3,
    thread_test_step_4, thread_test_step_5, add_comment_to_diary_entry)
                                                   

@unittest.skipIf(not formatter, "This test case needs django-markup, "
                 "docutils and markdown installed to be run")
class RenderMarkupValueFilterTestCase(DjangoTestCase):

    def test_render_markup_comment_in_markdown(self):
        comment = '#!markdown\nAn [example](http://url.com/ "Title")'
        result = render_markup_comment(comment)
        self.assertEqual(result,
                         '<p>An <a href="http://url.com/" title="Title">'
                         'example</a></p>')

    def test_render_markup_comment_in_restructuredtext(self):
        comment = ('#!restructuredtext\n'
                   'A fibonacci generator in Python, taken from '
                   '`LiteratePrograms <http://en.literateprograms.org/'
                   'Fibonacci_numbers_%28Python%29>`_::\n\n'
                   '    def fib():\n'
                   '        a, b = 0, 1\n'
                   '        while 1:\n'
                   '            yield a\n'
                   '            a, b = b, a + b')
        result = render_markup_comment(comment)
        self.assertEqual(result,
                         ('<div class="document">\n'
                          '<p>A fibonacci generator in Python, taken from '
                          '<a class="reference external" href="http://en.'
                          'literateprograms.org/Fibonacci_numbers_%28'
                          'Python%29">LiteratePrograms</a>:</p>\n'
                          '<pre class="literal-block">\n'
                          'def fib():\n'
                          '    a, b = 0, 1\n'
                          '    while 1:\n'
                          '        yield a\n'
                          '        a, b = b, a + b\n'
                          '</pre>\n'
                          '</div>\n'))


@unittest.skipIf(not formatter, "This test case needs django-markup, "
                 "docutils and markdown installed to be run")
class RenderFallbackMarkupValueFilterTestCase(DjangoTestCase):

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MARKUP_FALLBACK_FILTER='markdown')
    def test_render_fallback_markup_comment_markdown(self):
        with patch.multiple('django_comments_xtd.conf.settings',
                            COMMENTS_XTD_MARKUP_FALLBACK_FILTER='markdown'):
            comment = r'''An [example](http://url.com/ "Title")'''
            result = render_markup_comment(comment)
            self.assertEqual(result, '<p>An <a href="http://url.com/" '
                             'title="Title">example</a></p>')

    @patch.multiple('django_comments_xtd.conf.settings',
                    COMMENTS_XTD_MARKUP_FALLBACK_FILTER=None)
    def test_render_fallback_no_markup_comment(self):
        with patch.multiple('django_comments_xtd.conf.settings',
                            COMMENTS_XTD_MARKUP_FALLBACK_FILTER=None):
            comment = r'''An [example](http://url.com/ "Title")'''
            result = render_markup_comment(comment)
            self.assertEqual(result,
                             r'''An [example](http://url.com/ "Title")''')


@unittest.skipIf(formatter, "This test case needs django-markup or docutils "
                 "or markdown not installed to be run")
class MarkupNotAvailableTestCase(DjangoTestCase):

    def test_render_markup_comment(self):
        comment = r'''#!markdown
An [example](http://url.com/ "Title")'''
        render_markup_comment, comment
        self.assertRaises(TemplateSyntaxError, render_markup_comment, comment)


#----------------------------------------------------------------------
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
        
