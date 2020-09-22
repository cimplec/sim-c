import unittest
import sys

sys.path.append("..")

from token_class import Token

class TestTokenClass(unittest, TestCase):
    def setUp(self):
        self.token = Token("number", "8", 2)
        self.other = Token("number", "8", 2)

    def test__str__(self):
        self.assertEqual(str(self.token), "Token('number', '8', 2)")

    def test__eq__(self):
        self.assertEqual(self.token == self.other, True)

    def test_token2dig(self):
        self.assertEqual(self.token.token2dig("string"), 2)
        self.assertEqual(self.token.token2dig("multiply"), 11)
        self.assertEqual(self.token.token2dig("assignment"), 8)
        self.assertEqual(self.token.token2dig("while"), 22)
        self.assertEqual(self.token.token2dig("hello"), 0)
