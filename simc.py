# Standard library to take input as command line argument
import sys

# Module for using lexical analyzer
from lexical_analyzer import lexical_analyze

# Module for using parser
from parser import parse

# Module for using compiler
from compiler import compile

if __name__ == "__main__":
    # Get filename as command line argument
    filename = sys.argv[1]

    # Get the filename of c file to be generated
    c_filename = "".join(filename.split(".")[:-1]) + ".c"

    # Get tokens from lexical_analyzer
    tokens = lexical_analyze(filename)

    # Get opcodes from parser
    op_codes = parse(tokens)

    # Compile to C code
    compile(op_codes, c_filename)
