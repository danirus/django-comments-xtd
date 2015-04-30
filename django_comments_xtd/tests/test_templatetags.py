#-*- coding: utf-8 -*-

import unittest

from django.template import TemplateSyntaxError
from django.test import TestCase as DjangoTestCase

from django_comments_xtd.templatetags.comments_xtd import render_markup_comment, formatter


@unittest.skipIf(not formatter, "This test case needs django-markup, docutils and markdown installed to be run")
class RenderMarkupValueFilterTestCase(DjangoTestCase):

    def test_render_markup_comment_in_markdown(self):
        comment = r'''#!markdown
An [example](http://url.com/ "Title")'''
        result = render_markup_comment(comment)
        self.assertEqual(result,
                         '<p>An <a href="http://url.com/" title="Title">example</a></p>')

    def test_render_markup_comment_in_restructuredtext(self):
        comment = r'''#!restructuredtext
A fibonacci generator in Python, taken from `LiteratePrograms <http://en.literateprograms.org/Fibonacci_numbers_%28Python%29>`_::

    def fib():
        a, b = 0, 1
        while 1:
            yield a
            a, b = b, a + b'''
        result = render_markup_comment(comment)
        self.assertEqual(result,
                         r'''<p>A fibonacci generator in Python, taken from <a class="reference external" href="http://en.literateprograms.org/Fibonacci_numbers_%28Python%29">LiteratePrograms</a>:</p>
<pre class="literal-block">
def fib():
    a, b = 0, 1
    while 1:
        yield a
        a, b = b, a + b
</pre>
''')


@unittest.skipIf(formatter, "This test case needs django-markup or docutils or markdown not installed to be run")
class MarkupNotAvailableTestCase(DjangoTestCase):

    def test_render_markup_comment(self):
        comment = r'''#!markdown
An [example](http://url.com/ "Title")'''
        render_markup_comment, comment
        self.assertRaises(TemplateSyntaxError, render_markup_comment, comment)
