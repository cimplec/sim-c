import unittest
import sys

sys.path.append("..")

from simc.lexical_analyzer import lexical_analyze
from simc.symbol_table import SymbolTable
from simc.simc_parser import *


class TestSimcParser(unittest.TestCase):

    def test_function_definition(self):

        symbol_table = SymbolTable()
        tokens = lexical_analyze("data/add.simc", symbol_table)

        opcodes = parse(tokens, symbol_table)

        self.assertTrue(opcodes)

    def test_function_definition_w_default(self):

        symbol_table = SymbolTable()
        tokens = lexical_analyze("data/add_w_default.simc", symbol_table)

        opcodes = parse(tokens, symbol_table)

        self.assertTrue(opcodes)

    def test_function_definition_w_error(self):

        symbol_table = SymbolTable()
        tokens = lexical_analyze("data/add_err.simc", symbol_table)

        with self.assertRaises(SystemExit):
            parse(tokens, symbol_table)
