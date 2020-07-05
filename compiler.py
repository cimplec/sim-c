# Module to import OpCode class
from op_code import OpCode

def check_include(opcodes):
    """
        Params
        ======
        opcodes (list) = List of opcodes

        Returns
        =======
        The string representation of unique include files
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

def compile(opcodes, c_filename):
    """
        Params
        ======
        opcodes    (list)   = List of opcodes
        c_filename (string) = Name of C file to write C code into
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
        elif opcode.type == "var_assign":
            val = opcode.val.split('---')
            if(opcode.dtype == 'string'):
                opcode.dtype = 'char'
                val[0] += '[]'
            ccode += "\t" + opcode.dtype + " " + str(val[0]) + " = " + str(val[1]) + ";\n"
        elif opcode.type == "var_no_assign":
            opcode.dtype = str(opcode.dtype) if opcode.dtype is not None else "not_known"
            ccode += "\t" + opcode.dtype + " " + str(opcode.val) + ";\n"
        elif opcode.type == "assign":
            val = opcode.val.split('---')
            ccode += "\t" + val[0] + " = " + val[1] + ";\n"

    # Add return 0 to the end of code
    ccode += "\n\treturn 0;\n}"

    # Write generated code into C file
    with open(c_filename, "w") as file:
        file.write(ccode)
