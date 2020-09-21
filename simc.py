# Standard library to take input as command line argument
import sys

# Module to import Symbol Table class
from symbol_table import SymbolTable

# Module for using lexical analyzer
from lexical_analyzer import lexical_analyze

# Module for using parser
from simc_parser import parse

# Module for using compiler
from compiler import compile

if __name__ == "__main__":
    # Get filename as command line argument
    filename = sys.argv[1]

    # Get the filename of c file to be generated
    c_filename = "".join(filename.split(".")[:-1]) + ".c"

    # Create symbol table
    table = SymbolTable()

    # Get tokens from lexical_analyzer
    tokens = lexical_analyze(filename, table)

    if len(sys.argv) > 2 and sys.argv[2] == "tokens":
        for token in tokens:
            print(token)

    # Get opcodes from parser
    op_codes = parse(tokens, table)

    for op_code in op_codes:
        print(op_code)

    print(table.symbol_table)

    # Compile to C code
    compile(op_codes, c_filename, table)
