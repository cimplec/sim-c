# Import sys module
import sys

# Module to import global helpers
from .global_helpers import error

# Module to import Symbol Table class
from .symbol_table import SymbolTable

# Module for using lexical analyzer
from .lexical_analyzer import lexical_analyze

# Module for using parser
from .parser.simc_parser import parse

# Module for using compiler
from .compiler import compile

def run():
    filename = ""
    if(len(sys.argv) >= 2):
        filename = sys.argv[1]

        if "." not in filename or filename.split(".")[-1] != "simc":
            error("Incorrect file extension", -1)
    else:
        error("Please provide simc file path", -1)

    # Get the filename of c file to be generated
    c_filename = "".join(filename.split(".")[:-1]) + ".c"

    # Create symbol table
    table = SymbolTable()

    # Get tokens from lexical_analyzer
    tokens = lexical_analyze(filename, table)

    # Option to check out tokens
    if len(sys.argv) > 2 and sys.argv[2] == 'token':
        for token in tokens:
            print(token)

    # Get opcodes from parser
    op_codes = parse(tokens, table)

    # Option to check out opcodes
    if len(sys.argv) > 2 and sys.argv[2] == 'opcode':
        for op_code in op_codes:
            print(op_code)

    # Compile to C code
    compile(op_codes, c_filename, table)

    print("\033[92mC code generated at %s!" % c_filename, end="")
    print(" \033[m")