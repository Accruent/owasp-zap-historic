"""Unit tests for functions used in OWASP ZAP Historic small change"""
import datetime
import unittest

from owasp_zap_historic.app import convert_utc_to_cst


class TestFunctions(unittest.TestCase):
    """Unit Tests for functions"""

    def test_convert_utc_to_cst(self):
        """This test verifies that convert_utc_to_cst converts a datetime object within a tuple
        from assumed utc to cst time zone. """
        test_tuple = [("apple",
                       datetime.datetime(2020, 6, 4, 16, 14, 6, tzinfo=datetime.timezone.utc))]
        expected_tuple = "[('apple', datetime.datetime(2020, 6, 4, 11, 14, 6," + \
                         " tzinfo=<DstTzInfo 'US/Central' CDT-1 day, 19:00:00 DST>))]"
        result_tuple = convert_utc_to_cst(test_tuple)
        self.assertEqual(str(result_tuple), expected_tuple)

    def test_convert_utc_to_cst_no_date(self):
        """This test verifies that convert_utc_to_cst does not convert anything if the tuple
        does not contain a datetime object."""
        test_tuple = [("apple", 1.11, True), ("banana", 2.22, False)]
        result_tuple = convert_utc_to_cst(test_tuple)
        self.assertEqual(test_tuple, result_tuple)
