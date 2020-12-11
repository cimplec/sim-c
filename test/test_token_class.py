import unittest
import sys

sys.path.append("..")

from simc.token_class import Token

class TestTokenClass(unittest.TestCase):
    def setUp(self):
        self.token = Token("number", 1, 2)
        self.other = Token("number", 2, 2)

    def test__str__(self):
        self.assertEqual(str(self.token), "Token('number', '1', '2')")

    def test__eq__(self):
        self.assertTrue(self.token != self.other)

    def test_token2dig(self):
        self.assertEqual(self.token.token2dig("string"), 2)
        self.assertEqual(self.token.token2dig("multiply"), 11)
        self.assertEqual(self.token.token2dig("assignment"), 8)
        self.assertEqual(self.token.token2dig("while"), 22)
        self.assertEqual(self.token.token2dig("hello"), 0)
