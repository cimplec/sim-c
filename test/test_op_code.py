import unittest
import sys

sys.path.append('..')

from op_code import OpCode

class TestOpCodeClass(unittest.TestCase):

    def setUp(self):
        self.opcode = OpCode("var_assign", "a---1 + 2", "int")

    def test__str__(self):
        self.assertEqual(str(self.opcode), "OpCode('var_assign', 'a---1 + 2', 'int')")

    def test_opcode2dig(self):
        self.assertEqual(self.opcode.opcode2dig("var_assign"), 2)
        self.assertEqual(self.opcode.opcode2dig("unary"), 12)
        self.assertEqual(self.opcode.opcode2dig("hello"), 0)
