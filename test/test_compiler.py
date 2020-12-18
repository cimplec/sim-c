import unittest
import os
import sys

sys.path.append("..")

from simc.op_code import OpCode
from simc.symbol_table import SymbolTable
from simc.compiler import *


class TestCompiler(unittest.TestCase):
    def test_check_include_print(self):
        opcodes = [OpCode("print", '"%d", a', "None")]

        includes = check_include(opcodes)
        self.assertEqual(includes, "#include <stdio.h>")

    def test_check_include_input(self):
        opcodes = [OpCode("var_assign", "a---Enter a number: ---i", "int")]

        includes = check_include(opcodes)
        self.assertEqual(includes, "#include <stdio.h>")

    def test_check_include_math_constant(self):
        opcodes = [OpCode("print", '"%lf", M_PI', "None")]

        includes = check_include(opcodes)
        includes = set(includes.split("\n"))
        self.assertEqual(includes, set(["#include <stdio.h>", "#include <math.h>"]))

    def test_check_include_no_includes(self):
        opcodes = [OpCode("var_assign", "b---2", "int")]

        includes = check_include(opcodes)
        self.assertEqual(includes, "")

    def test_compile_func_main_code_inside_main(self):
        outside_code = ""
        ccode = ""

        outside_main = False
        code = "Hello World"

        outside_code, ccode = compile_func_main_code(
            outside_code, ccode, outside_main, code
        )

        self.assertEqual(ccode, "Hello World")

    def test_compile_func_main_code_outside_main(self):
        outside_code = ""
        ccode = ""

        outside_main = True
        code = "Test simC"

        outside_code, ccode = compile_func_main_code(
            outside_code, ccode, outside_main, code
        )

        self.assertEqual(outside_code, "Test simC")

    def test_compile_print(self):
        opcodes = [OpCode("print", '"%d", 1')]
        table = SymbolTable()

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["#include <stdio.h>", '\tprintf("%d", 1);', ""])

    def test_compile_var_assign(self):
        opcodes = [OpCode("var_assign", "a---1 + 2", "int")]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "int", "variable"],
            2: ["1", "int", "constant"],
            3: ["2", "int", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "\tint a = 1 + 2;", ""])

    def test_compile_ptr_assign(self):
        opcodes = [
            OpCode("var_assign", "a---1", "int"),
            OpCode("ptr_assign", "n---&a---1", "int"),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "int", "variable"],
            2: ["1", "int", "constant"],
            3: ["n", "int", "variable"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data, ["#include <stdio.h>", "\tint a = 1;", "\tint *n = &a;", ""]
        )

    def test_compile_var_no_assign(self):
        opcodes = [OpCode("var_no_assign", "a", None)]
        table = SymbolTable()
        table.symbol_table = {1: ["a", "declared", "variable"]}

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "\tdeclared a;", ""])

    def test_compile_ptr_no_assign(self):
        opcodes = [OpCode("ptr_no_assign", "a", None)]
        table = SymbolTable()
        table.symbol_table = {1: ["a", "declared", "variable"]}

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "\tdeclared *a;", ""])

    def test_compile_assign(self):
        opcodes = [
            OpCode("var_no_assign", "a", None),
            OpCode("assign", "a---=---3.14159", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "float", "variable"],
            2: ["3.14159", "float", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data, ["#include <stdio.h>", "\tfloat a;", "\ta = 3.14159;", ""]
        )

    def test_compile_ptr_only_assign(self):
        ## TODO: Fix this test after bug #23 gets fixed
        opcodes = [
            OpCode("var_assign", "a---1", "int"),
            OpCode("ptr_assign", "n---&a---1", "int"),
            OpCode("ptr_only_assign", "n---=---2---1", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "int", "variable"],
            2: ["1", "int", "constant"],
            3: ["n", "int", "variable"],
            4: ["2", "int", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            ["#include <stdio.h>", "\tint a = 1;", "\tint *n = &a;", "\t**n = =;", ""],
        )

    def test_compile_unary(self):
        opcodes = [OpCode("var_assign", "a---1", "int"), OpCode("unary", "a ++ ", None)]
        table = SymbolTable()
        table.symbol_table = {1: ["a", "int", "variable"], 2: ["1", "int", "constant"]}

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "\tint a = 1;", "\ta++;", ""])

    def test_compile_func_decl(self):
        # This also tests scope_begin and scope_over

        opcodes = [
            OpCode("func_decl", "hello---", ""),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"World"', None),
            OpCode("scope_over", "", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["hello", "var", "function"],
            2: ['"World"', "string", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "",
                "void hello(void) {",
                '\tprintf("World");',
                "}",
                "",
            ],
        )

    def test_compile_func_call(self):
        # This also tests scope_begin and scope_over

        opcodes = [
            OpCode("func_decl", "hello---", ""),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"World"', None),
            OpCode("scope_over", "", ""),
            OpCode("func_call", "hello---", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["hello", "var", "function"],
            2: ['"World"', "string", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "",
                "void hello(void) {",
                '\tprintf("World");',
                "}",
                "\thello();",
                "",
            ],
        )

    def test_compile_main_end_main(self):
        opcodes = [OpCode("MAIN", "", ""), OpCode("END_MAIN", "", "")]
        table = SymbolTable()

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "", "int main() {", "", "\treturn 0;", "}", ""])

    def test_compile_for(self):
        opcodes = [
            OpCode("for", "i&&&1&&&10&&&+&&&<&&&1", None),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"%d", i', None),
            OpCode("scope_over", "", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["i", "int", "variable"],
            2: ["1", "int", "constant"],
            3: ["10", "int", "constant"],
            4: ["1", "int", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "\tfor(int i = 1; i < 10; i+=1) {",
                '\tprintf("%d", i);',
                "}",
                "",
            ],
        )

    def test_compile_while(self):
        opcodes = [
            OpCode("var_assign", "i---0", "int"),
            OpCode("while", "i < 10", None),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"%d", i', None),
            OpCode("scope_over", "", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["i", "int", "variable"],
            2: ["0", "int", "constant"],
            3: ["10", "int", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "\tint i = 0;",
                "\twhile(i < 10) {",
                '\tprintf("%d", i);',
                "}",
                "",
            ],
        )

    def test_compile_do_while_do(self):
        # Testing do while loop (both the do part and the while part)

        opcodes = [
            OpCode("var_assign", "i---0", "int"),
            OpCode("do", "", ""),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"%d", i', None),
            OpCode("scope_over", "", ""),
            OpCode("while_do", "i <= 0", None),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["i", "int", "variable"],
            2: ["0", "int", "constant"],
            3: ["0", "int", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "\tint i = 0;",
                "\tdo {",
                '\tprintf("%d", i);',
                "}",
                "\twhile(i <= 0);",
            ],
        )

    def test_compile_if_else_if_else(self):
        # Testing if, else if, else

        opcodes = [
            OpCode("var_assign", "i---0", "int"),
            OpCode("if", "i == 1", None),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"%d", 1', None),
            OpCode("scope_over", "", ""),
            OpCode("else_if", "i == 2", None),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"%d", 2', None),
            OpCode("scope_over", "", ""),
            OpCode("else", "", ""),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"Else"', None),
            OpCode("scope_over", "", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["i", "int", "variable"],
            2: ["0", "int", "constant"],
            3: ["1", "int", "constant"],
            4: ["1", "int", "constant"],
            5: ["2", "int", "constant"],
            6: ["2", "int", "constant"],
            7: ['"Else"', "string", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "\tint i = 0;",
                "\tif(i == 1) {",
                '\tprintf("%d", 1);',
                "}",
                "\telse if(i == 2) {",
                '\tprintf("%d", 2);',
                "}",
                "\telse {",
                '\tprintf("Else");',
                "}",
                "",
            ],
        )

    def test_compile_exit(self):
        opcodes = [OpCode("exit", "0", None)]
        table = SymbolTable()
        table.symbol_table = {1: ["0", "int", "constant"]}

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "\texit(0);", ""])

    def test_compile_return(self):
        opcodes = [
            OpCode("func_decl", "hello---", ""),
            OpCode("scope_begin", "", ""),
            OpCode("return", "1", ""),
            OpCode("scope_over", "", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["hello", "int", "function"],
            2: ["1", "int", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data, ["", "", "int hello(void) {", "", "\treturn 1;", "}", ""]
        )

    def test_compile_continue_break(self):
        # Test continue and break statements

        opcodes = [OpCode("continue", "", ""), OpCode("break", "", "")]
        table = SymbolTable()

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(data, ["", "\tcontinue;", "\tbreak;", ""])

    def test_compile_single_multi_line_comments(self):
        # Test single and multi line comments

        opcodes = [
            OpCode("single_line_comment", " single line", ""),
            OpCode(
                "multi_line_comment",
                """
                    Multi line
                    """,
                "",
            ),
        ]
        table = SymbolTable()

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "",
                "\t//  single line ",
                "/* ",
                "                    Multi line",
                "                    */",
                "",
            ],
        )

    def test_compile_switch_case_default(self):
        # Test swtich, case, and default statements

        opcodes = [
            OpCode("var_assign", "a---1", "int"),
            OpCode("switch", "a", ""),
            OpCode("scope_begin", "", ""),
            OpCode("case", "1", ""),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"Hello"', None),
            OpCode("scope_over", "", ""),
            OpCode("default", "", ""),
            OpCode("scope_begin", "", ""),
            OpCode("print", '"Bye"', None),
            OpCode("scope_over", "", ""),
            OpCode("scope_over", "", ""),
        ]
        table = SymbolTable()
        table.symbol_table = {
            1: ["a", "int", "variable"],
            2: ["1", "int", "constant"],
            3: ["1", "int", "constant"],
            4: ['"Hello"', "string", "constant"],
            5: ['"Bye"', "string", "constant"],
        }

        compile(opcodes, "testing.c", table)

        with open("testing.c", "r") as file:
            data = file.read().split("\n")

        os.remove("testing.c")

        self.assertEqual(
            data,
            [
                "#include <stdio.h>",
                "\tint a = 1;",
                "\tswitch(a) {",
                "\tcase 1:",
                "{",
                '\tprintf("Hello");',
                "}",
                "\tdefault:",
                "{",
                '\tprintf("Bye");',
                "}",
                "}",
                "",
            ],
        )
