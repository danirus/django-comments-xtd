import unittest


def suite():
    from django_comments_xtd.tests import forms, views

    testsuite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromModule(models),
        unittest.TestLoader().loadTestsFromModule(forms),
        unittest.TestLoader().loadTestsFromModule(views),
    ])
    return testsuite
