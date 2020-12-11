# Import sys and os module
import sys
import os

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
    tokens, module_source_paths = lexical_analyze(filename, table)

    # Lexical analysis of all imports
    all_module_tokens = {}
    if len(module_source_paths) > 0:
        for module_source_path in module_source_paths:
            module_name = os.path.basename(module_source_path).split(".")[0]
            all_module_tokens[module_name], _ = lexical_analyze(module_source_path, table)

    # Option to check out tokens
    if len(sys.argv) > 2 and sys.argv[2] == 'token':
        for token in tokens:
            print(token)

        for module_name, module_tokens in all_module_tokens.items():
            print("\n---Tokens for module " + module_name + "---")
            for token in module_tokens:
                print(token)

    # Parse the imports first
    all_module_opcodes = {}

    for module_name, module_tokens in all_module_tokens.items():
        all_module_opcodes[module_name] = parse(module_tokens, table)

    # Get opcodes from parser
    op_codes = parse(tokens, table)

    # Option to check out opcodes
    if len(sys.argv) > 2 and sys.argv[2] == 'opcode':
        for op_code in op_codes:
            print(op_code)

        for module_name, module_opcodes in all_module_opcodes.items():
            print("\n---OpCodes for module " + module_name + "---")
            for op_code in module_opcodes:
                print(op_code)

    # Compile to C code
    compile(op_codes, c_filename, table)

    # Compile the module functions
    for module_name, module_opcodes in all_module_opcodes.items():
        module_c_filename = module_name + ".h"

        compile(module_opcodes, module_c_filename, table)

    print("\033[92mC code generated at %s!" % c_filename, end="")
    print(" \033[m")