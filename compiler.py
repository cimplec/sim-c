# Module to import OpCode class
from op_code import OpCode

def check_include(opcodes):
    """
        Checks if any opcode requires standard libraries to be included

        Params
        ======
        opcodes (list) = List of opcodes

        Returns
        =======
        string: The string representation of unique include files
    """

    # List of includes
    includes = []

    # Loop through all opcodes
    for opcode in opcodes:
        # If opcode is of type print, then it requires stdio.h to be included
        if(opcode.type == "print"):
            includes.append("#include <stdio.h>")

    # Return string representation of unique elements of includes list separated by newline characters
    return "\n".join(list(set(includes)))

def compile(opcodes, c_filename, table):
    """
        Compiles opcodes produced by parser into C code

        Params
        ======
        opcodes    (list)        = List of opcodes
        c_filename (string)      = Name of C file to write C code into
        table      (SymbolTable) = Symbol table constructed during lexical analysis and parsing
    """

    # Check for includes
    ccode = check_include(opcodes) + "\n"

    # Put the code in main function
    ccode += "\nint main() {\n"

    # Loop through all opcodes
    for opcode in opcodes:
        # If opcode is of type print then generate a printf statement
        if opcode.type == "print":
            ccode += "\tprintf(%s);\n" % opcode.val
        # If opcode is of type var_assign then generate a declaration [/initialization] statement
        elif opcode.type == "var_assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            # Get the datatye of the variable
            _, dtype, _ = table.get_by_id(table.get_by_symbol(val[0]))

            # If it is of string type then change it to char <identifier>[]
            if(dtype == 'string'):
                dtype = 'char'
                val[0] += '[]'

            ccode += "\t" + dtype + " " + str(val[0]) + " = " + str(val[1]) + ";\n"
        # If opcode is of type var_no_assign then generate a declaration statement
        elif opcode.type == "var_no_assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            # Get the datatye of the variable
            _, dtype, _ = table.get_by_id(table.get_by_symbol(val[0]))

            # Check if dtype could be inferred or not
            opcode.dtype = str(dtype) if dtype is not None else "not_known"

            ccode += "\t" + opcode.dtype + " " + str(opcode.val) + ";\n"
        # If opcode is of type assign then generate an assignment statement
        elif opcode.type == "assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            ccode += "\t" + val[0] + " = " + val[1] + ";\n"

    # Add return 0 to the end of code
    ccode += "\n\treturn 0;\n}"

    # Write generated code into C file
    with open(c_filename, "w") as file:
        file.write(ccode)
