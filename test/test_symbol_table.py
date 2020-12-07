import unittest
import sys

sys.path.append('..')

from simc.symbol_table import SymbolTable

class TestSymbolTableClass(unittest.TestCase):

    def setUp(self):
        self.table = SymbolTable()

    def test_entry(self):
        id_1 = self.table.entry("hello", "int", "variable")
        id_2 = self.table.entry("world", "float", "constant")

        self.assertEqual(id_1, 1)
        self.assertEqual(id_2, 2)

        self.assertEqual(self.table.symbol_table, {1: ["hello", "int", "variable"], 2: ["world", "float", "constant"]})

    def test_get_by_id(self):
        id_1 = self.table.entry("hello", "int", "variable")
        id_2 = self.table.entry("world", "float", "constant")

        value, type, typedata = self.table.get_by_id(2)

        self.assertEqual(value, "world")
        self.assertEqual(type, "float")
        self.assertEqual(typedata, "constant")

        value, type, typedata = self.table.get_by_id(10)

        self.assertEqual(value, None)
        self.assertEqual(type, None)
        self.assertEqual(typedata, None)

    def test_get_symbol(self):
        id_1 = self.table.entry("hello", "int", "variable")
        id_2 = self.table.entry("world", "float", "constant")

        id = self.table.get_by_symbol("world")

        self.assertEqual(id, 2)

        id = self.table.get_by_symbol("something")

        self.assertEqual(id, -1)
