try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase


class GetVersionTestCase(TestCase):

    @patch('django_comments_xtd.VERSION', (2, 8, 0, 'f', 0))
    def test_get_version_when_patch_equal_to_zero(self):
        from django_comments_xtd import get_version
        self.assertEqual(get_version(), '2.8.0')

    @patch('django_comments_xtd.VERSION', (2, 8, 1, 'f', 0))
    def test_get_version_when_patch_greater_than_zero(self):
        from django_comments_xtd import get_version
        self.assertEqual(get_version(), '2.8.1')

    @patch('django_comments_xtd.VERSION', (2, 8, 1, 9, 8))
    def test_get_version_when_version_three_not_f(self):
        from django_comments_xtd import get_version
        self.assertEqual(get_version(), '2.8.198')
