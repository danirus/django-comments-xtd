import unittest


def suite():
    from django_comments_xtd.tests import forms, models, templatetags, views

    testsuite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromModule(models),
        unittest.TestLoader().loadTestsFromModule(forms),
        unittest.TestLoader().loadTestsFromModule(views),
        unittest.TestLoader().loadTestsFromModule(templatetags),
    ])
    return testsuite
