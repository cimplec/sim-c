import unittest
import sys

sys.path.append("..")

from symbol_table import SymbolTable
from token_class import Token
from lexical_analyzer import *


class TestLexicalAnalyzer(unittest.TestCase):
    def test_is_keyword(self):
        self.assertEqual(is_keyword("fun"), True)
        self.assertEqual(is_keyword("exit"), True)
        self.assertEqual(is_keyword("hello"), False)

    def test_numeric_val_float(self):
        source_code = "3.14\0"
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = numeric_val(source_code, i, table, line_num)
        other = Token("number", 1, 1)

        self.assertEqual(token, other)

        self.assertEqual(table.symbol_table, {1: ["3.14", "float", "constant"]})

    def test_numeric_val_double(self):
        source_code = "3.1415914159\0"
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = numeric_val(source_code, i, table, line_num)
        other = Token("number", 1, 1)

        self.assertEqual(token, other)

        self.assertEqual(
            table.symbol_table, {1: ["3.1415914159", "double", "constant"]}
        )

    def test_numeric_val_int(self):
        source_code = "3\0"
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = numeric_val(source_code, i, table, line_num)
        other = Token("number", 1, 1)

        self.assertEqual(token, other)

        self.assertEqual(table.symbol_table, {1: ["3", "int", "constant"]})

    def test_string_val_string(self):
        source_code = '"hello"\\0'
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = string_val(source_code, i, table, line_num)

        other = Token("string", 1, 1)

        self.assertEqual(token, other)

        self.assertEqual(table.symbol_table, {1: ['"hello"', "string", "constant"]})

    def test_string_val_char(self):
        source_code = '"h"\\0'
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = string_val(source_code, i, table, line_num)

        other = Token("string", 1, 1)

        self.assertEqual(token, other)

        self.assertEqual(table.symbol_table, {1: ["'h'", "char", "constant"]})

    def test_keyword_identifier_keyword(self):
        # Test a keyword

        source_code = "fun\\0"
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = keyword_identifier(source_code, i, table, line_num)

        other = Token("fun", "", 1)

        self.assertEqual(token, other)

    def test_keyword_identifier_identifier(self):
        # Test an identifier

        source_code = "a\\0"
        i = 0
        table = SymbolTable()
        line_num = 1

        token, _ = keyword_identifier(source_code, i, table, line_num)

        other = Token("id", 1, 1)

        self.assertEqual(token, other)

        self.assertEqual(table.symbol_table, {1: ["a", "var", "variable"]})

    def test_lexical_analyze_left_right_paren_call_end(self):
        # Test left_paren, right_paren, and call_end

        source_code = "var a = (1)"
        with open("testing.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        tokens = lexical_analyze("testing.simc", table)

        left_paren = Token("left_paren", "", 1)
        right_paren = Token("right_paren", "", 1)
        call_end = Token("call_end", "", 1)

        self.assertEqual(tokens[3], left_paren)
        self.assertEqual(tokens[5], right_paren)
        self.assertEqual(tokens[6], call_end)

    def test_lexical_analyze_left_right_brace_newline(self):
        # Test left_brace, right_brace, and newline

        source_code = """if(1 == 1) {
          print(1)
        }
        """
        with open("testing.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        tokens = lexical_analyze("testing.simc", table)

        left_brace = Token("left_brace", "", 1)
        right_brace = Token("right_brace", "", 3)
        newline = Token("newline", "", 1)

        self.assertEqual(tokens[7], left_brace)
        self.assertEqual(tokens[-2], right_brace)
        self.assertEqual(tokens[8], newline)

    def test_lexical_analyze_assignment_equal(self):
        # Test assignment and equal

        source_code = "var a = 1 == 1"

        with open("testing.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        tokens = lexical_analyze("testing.simc", table)

        assignment = Token("assignment", "", 1)
        equal = Token("equal", "", 1)

        self.assertEqual(tokens[2], assignment)
        self.assertEqual(tokens[-2], equal)

    def test_lexical_analyze_plus_equal_increment_plus(self):
        # Test plus_equal, increment, and plus

        source_code = """var a = 1 + 2
        a += 1
        a++
        """

        with open("testing.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        tokens = lexical_analyze("testing.simc", table)

        plus_equal = Token("plus_equal", "", 2)
        increment = Token("increment", "", 3)
        plus = Token("plus", "", 1)

        self.assertEqual(tokens[8], plus_equal)
        self.assertEqual(tokens[12], increment)
        self.assertEqual(tokens[4], plus)

    def test_lexical_analyze_minus_equal_decrement_minus(self):
        # Test minus_equal, decrement, and minus

        source_code = """var a = 1 - 2
        a -= 1
        a--
        """

        with open("testing.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        tokens = lexical_analyze("testing.simc", table)

        minus_equal = Token("minus_equal", "", 2)
        decrement = Token("decrement", "", 3)
        minus = Token("minus", "", 1)

        self.assertEqual(tokens[8], minus_equal)
        self.assertEqual(tokens[12], decrement)
        self.assertEqual(tokens[4], minus)

    def test_lexical_analyze_multiply_equal_multiply(self):
        # Test multiply_equal and multiply

        source_code = """var a = 1 * 2
        a *= 1
        """

        with open("testing.simc", "w") as file:
            file.write(source_code)

        table = SymbolTable()

        tokens = lexical_analyze("testing.simc", table)

        multiply_equal = Token("multiply_equal", "", 2)
        multiply = Token("multiply", "", 1)

        self.assertEqual(tokens[8], multiply_equal)
        self.assertEqual(tokens[4], multiply)
