# Import sys module
import sys

# Module to import global helpers
from .global_helpers import error

# Module to import Symbol Table class
from .symbol_table import SymbolTable

# Module for using lexical analyzer
from .lexical_analyzer import lexical_analyze

# Module for using parser
from .simc_parser import parse

# Module for using compiler
from .compiler import compile

def run():
    filename = ""
    if(len(sys.argv) == 2):
        filename = sys.argv[1]

        if "." not in filename or filename.split(".")[-1] != "simc":
            error("Incorrect file extension", line_num)
    else:
        error("Please provide simc file path", -1)

    # Get the filename of c file to be generated
    c_filename = "".join(filename.split(".")[:-1]) + ".c"

    # Create symbol table
    table = SymbolTable()

    # Get tokens from lexical_analyzer
    tokens = lexical_analyze(filename, table)

    # Get opcodes from parser
    op_codes = parse(tokens, table)

    # Compile to C code
    compile(op_codes, c_filename, table)

    print("\033[92mC code generated at filename!")
