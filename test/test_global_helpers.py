import unittest
import sys

sys.path.append("..")

from global_helpers import *


class TestGlobalHelpers(unittest.TestCase):
    def test_is_digit(self):
        self.assertEqual(is_digit("6"), True)
        self.assertEqual(is_digit("$"), False)
        self.assertEqual(is_digit("a"), False)

    def test_is_alpha(self):
        self.assertEqual(is_alpha("a"), True)
        self.assertEqual(is_alpha("Z"), True)
        self.assertEqual(is_alpha("_"), True)
        self.assertEqual(is_alpha("1"), False)
        self.assertEqual(is_alpha("@"), False)

    def test_is_alnum(self):
        self.assertEqual(is_alnum("a"), True)
        self.assertEqual(is_alnum("Z"), True)
        self.assertEqual(is_alnum("_"), True)
        self.assertEqual(is_alnum("1"), True)
        self.assertEqual(is_alnum("@"), False)
