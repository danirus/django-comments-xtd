import unittest


def suite():
    from django_comments_xtd.tests import (test_forms, test_models,
                                           test_templatetags, test_views)

    testsuite = unittest.TestSuite([
        unittest.TestLoader().loadTestsFromModule(test_models),
        unittest.TestLoader().loadTestsFromModule(test_forms),
        unittest.TestLoader().loadTestsFromModule(test_views),
        unittest.TestLoader().loadTestsFromModule(test_templatetags),
    ])
    return testsuite
