# Module to import OpCode class
from .op_code import OpCode


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

    # List of math constants
    math_func_const = ["M_PI", "M_E", "pow(", "INFINITY", "NAN"]

    # Loop through all opcodes
    for opcode in opcodes:
        # If opcode is of type print, then it requires stdio.h to be included
        if opcode.type == "print":
            includes.append("#include <stdio.h>")

        # If there is any boolean assignment opcode then include stdbool.h
        if opcode.dtype == "bool":
            includes.append("#include <stdbool.h>")

        # If the opcode is a statement of type input, then it requires stdio.h to be included
        if len(opcode.val.split("---")) >= 3:
            includes.append("#include <stdio.h>")

        if any(math in opcode.val for math in math_func_const):
            includes.append("#include <math.h>")

    # Return string representation of unique elements of includes list separated by newline characters
    return "\n".join(list(set(includes)))


def compile_func_main_code(outside_code, ccode, outside_main, code):
    """
    Check which code should go in main and which outside of main

    Params
    ======
    outside_code (string)        = Code to be put outside main function
    ccode        (string)        = Code to be put inside main function
    outside_main (bool)          = Decides where the code should go (true - outside, false - inside)
    code         (string)        = Compiled code

    Returns
    =======
    string, string: The outside and main C code strings
    """

    # If outside_main is true then code goes outside main
    if outside_main:
        outside_code += code
    else:
        if code == "}\n":
            code = "\t" + code
        ccode += code

    # Return code strings
    return outside_code, ccode


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
    compiled_code = check_include(opcodes) + "\n"

    # Put the code in main function
    ccode = ""

    # Function code is compiled into separate list
    outside_code = ""

    # Check if function body has started or not
    outside_main = True

    # Check if the function has returned or not
    has_returned = False
    
    # Loop through all opcodes
    for opcode in opcodes:
        code = ""
        # If opcode is of type print then generate a printf statement
        if opcode.type == "print":

            if (
                opcode.val == '"%s", i'
            ):  # Temporary solution to the printf( ) statement being used on strings
                opcode.val = '"%s", &i'
                # Generation of opcode is flawed as it fails to add the reference addess of the string being printed

            code = "\tprintf(%s);\n" % opcode.val

        # If opcode is of type import then generate include statement
        if opcode.type == "import":
            code = '#include "' + opcode.val + '.h"\n'

        # If opcode is of type var_assign then generate a declaration [/initialization] statement
        elif opcode.type == "var_assign":
            code = ""

            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split("---")
            # Get the datatye of the variable
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))

            # Helper Dictionaries
            get_data_type = {
                "i": "int",
                "s": "char*",
                "f": "float",
                "d": "double",
                "c": "char",
            }
            get_placeholder = {"i": "d", "s": "s", "f": "f", "d": "lf", "c": "c"}

            # If it is of string type then change it to char <identifier>[]
            if dtype == "string":
                dtype = "char*"
            # Check if the statement is of type input or not
            if len(val) < 3:
                code += "\t" + dtype + " " + str(val[0]) + " = " + str(val[1]) + ";\n"
            else:
                # If the statement is of type input -
                dtype = get_data_type[val[2]]
                placeholder = get_placeholder[val[2]]
                code += "\t" + dtype + " " + str(val[0]) + ";\n"
                if val[1] != "":
                    code += "\t" + 'printf("' + str(val[1]) + '");\n'
                code += "\t" + 'scanf("%' + placeholder

                if dtype == "char*":
                    # If the datatype is character array, we need to pass in the reference address into scanf( )
                    code += '", &' + str(val[0]) + ");\n"
                elif "*" in dtype:
                    code += '", ' + str(val[0]) + ");\n"
                else:
                    code += '", &' + str(val[0]) + ");\n"
        # If opcode is of type ptr_assign then generate a declarative statement
        elif opcode.type == "ptr_assign":
            code = ""

            # val contains - <identifier>---<expression>---<count_ast>, split that into a list
            val = opcode.val.split("---")

            # Get the datatye of the variable
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))

            # Helper Dictionaries
            get_data_type = {
                "i": "int",
                "s": "char*",
                "f": "float",
                "d": "double",
                "c": "char",
            }
            get_placeholder = {"i": "d", "s": "s", "f": "f", "d": "lf", "c": "c"}

            # If it is of string type then change it to char <identifier>[]
            if dtype == "string":
                dtype = "char*"
            code += (
                "\t"
                + dtype
                + " "
                + "*" * int(val[2])
                + str(val[0])
                + " = "
                + str(val[1])
                + ";\n"
            )

        # If opcode is of type var_no_assign then generate a declaration statement
        elif opcode.type == "var_no_assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split("---")

            # Get the datatye of the variable
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))
            # Check if dtype could be inferred or not
            opcode.dtype = str(dtype) if dtype is not None else "not_known"
            code += "\t" + opcode.dtype + " " + str(opcode.val) + ";\n"
        elif opcode.type == "array_no_assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split("---")
            # Get the datatye of the variable
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))
            # Check if dtype could be inferred or not
            opcode.dtype = str(dtype) if dtype is not None else "not_known"
            code += (
                "\t" + opcode.dtype + " *" + str(val[0]) + ";\n"
            )
        elif opcode.type == "array_assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split("---")
            # Get the datatye of the variable
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))
            # Check if dtype could be inferred or not
            opcode.dtype = str(dtype) if dtype is not None else "not_known"
            code += (
                "\t"
                + opcode.dtype
                + " "
                + str(val[0])
                + "["
                + (val[1])
                + "]"
                + " = "
                + val[2]
                + ";\n"
            )
        elif opcode.type == "array_only_assign":
            # val contains - <identifier>---=(<type> [<size>])<initializer-list>, split that into a list
            val = opcode.val.split("---")

            # val[0] contains identifier and val[1] contains =(<type> [<size>])<initializer-list>
            code += "\t" + val[0] + val[1] + ";\n"
        # If opcode is of type ptr_no_assign then generate declaration statement
        elif opcode.type == "ptr_no_assign":
            val = opcode.val.split("---")
            # Get the datatye of the variable
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))
            # Check if dtype could be inferred or not
            opcode.dtype = str(dtype) if dtype is not None else "not_known"
            if opcode.dtype == "string":
                opcode.dtype = "char"
            code += "\t" + opcode.dtype + " *" + str(opcode.val) + ";\n"

        # If opcode is of type assign then generate an assignment statement
        elif opcode.type == "assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split("---")
            # Helper Dictionaries
            get_data_type = {
                "i": "int",
                "s": "char *",
                "f": "float",
                "d": "double",
                "c": "char",
            }
            get_placeholder = {"i": "d", "s": "s", "f": "f", "d": "lf", "c": "c"}
            # Check if the statement is of type input or not
            if len(val) == 3:
                code += "\t" + val[0] + " " + val[1] + " " + val[2] + ";\n"
            else:
                # If the statement is of type input
                dtype = get_data_type[val[3]]
                placeholder = get_placeholder[val[3]]
                if val[2] != "":
                    code += "\t" + 'printf("' + str(val[2]) + '");\n'
                code += "\t" + 'scanf("%' + placeholder + '", &' + str(val[0]) + ");\n"

        # If opcode is of type ptr_only_assign then generate an assignment statement
        elif opcode.type == "ptr_only_assign":
            # val contains - <identifier>---<expression>---<count_ast>, split that into a list
            val = opcode.val.split("---")
            code += "\t" + int(val[3]) * "*" + val[0] + " = " + val[2] + ";\n"

        # If opcode is of type unary then generate an uanry statement
        elif opcode.type == "unary":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split("---")
            print_val = ""
            for i in val:
                i = i.replace(" ", "")
                print_val += str(i)
            code += "\t" + print_val + ";\n"
        # If opcode is of type func_decl then generate function declaration statement
        elif opcode.type == "func_decl":
            # val contains - <identifier>---<params>, split that into list
            val = opcode.val.split("---")

            # Check if function has params
            params = val[1].split("&&&") if len(val[1]) > 0 else []

            # Get the return type of the function
            _, dtype, _, _ = table.get_by_id(table.get_by_symbol(val[0]))
            dtype = dtype if dtype != "var" else "void"

            # Append the function return type and name to code
            code += "\n" + dtype + " " + val[0] + "("

            # Compile the formal params
            has_param = False
            for i in range(len(params)):
                if len(params[i]) > 0:
                    has_param = True
                    _, dtype, _, _ = table.get_by_id(table.get_by_symbol(params[i]))
                    dtype = dtype if dtype != "var" else "not_known"
                    dtype = "char*" if dtype == "string" else dtype
                    code += dtype + " " + params[i] + ", "
            if has_param:
                code = code[:-2]
            else:
                code += "void"

            # Finally add opening brace to start the function body
            code += ") "
        # If the opcode is of type func_call then generate function calling statement
        elif opcode.type == "func_call":
            # val contains - <identifier>---<params>, split that into list
            val = opcode.val.split("---")

            # Check if function has params
            params = val[1].split("&&&") if len(val[1]) > 0 else []

            # Compile function name
            code = "\t" + val[0] + "("

            # Compile the actual params
            has_param = False
            for param in params:
                if len(params) > 0:
                    has_param = True
                    code += param + ", "
            if has_param:
                code = code[:-2]

            # Finally add opening brace to start the function body
            code += ");\n"
        # If opcode is of type struct_decl then generate structure declaration statement
        elif opcode.type == "struct_decl":
            # extracting struct name from val
            struct_name = opcode.val

            # append the struct keyword and structure nameto the code
            code += "\n" + "struct" + " " + struct_name + " "
        # If opcode is of type struct_instantiate then generate structure instantiation statement
        elif opcode.type == "struct_instantiate":
            # Extract the identifier name of instance variable
            struct_name, instance_var_name = opcode.val.split("---")

            code += "\t" + "struct " + struct_name.strip() + " " + instance_var_name.strip() + ";\n"
        # If opcode is of type scope_begin then generate open brace statement
        elif opcode.type == "scope_begin":
            code += "{\n"
        # If opcode is of type scope_over then generate closing brace statement
        elif opcode.type == "scope_over":
            code += "}\n"
        # If opcode is of type struct_scope_over then generate closing brace, name of struct instance (if any) and add a semi-colon
        elif opcode.type == "struct_scope_over":
            code += "} " + opcode.val + ";\n"
        # If opcode is of type scope_over then generate closing brace statement
        elif opcode.type == "MAIN":
            code += "\nint main() {\n"
            outside_main = False
            has_returned = False
        # If opcode is of type scope_over then generate closing brace statement
        elif opcode.type == "END_MAIN":
            if not has_returned:
                code += "\n\treturn 0;"
            code += "\n}\n"
            outside_code, ccode = compile_func_main_code(
                outside_code, ccode, outside_main, code
            )
            outside_main = True
            continue
        # If opcode is of type for
        elif opcode.type == "for":
            val = opcode.val.split("&&&")
            code += (
                "\tfor(int "
                + val[0]
                + " = "
                + val[1]
                + "; "
                + val[0]
                + " "
                + val[4]
                + " "
                + val[2]
                + "; "
                + val[0]
                + val[3]
                + "="
                + val[5]
                + ") "
            )
        # If opcode is of type while then generate while loop statement
        elif opcode.type == "while":
            code = "\twhile(%s) " % opcode.val
        # If opcode is of type do then generate do statement
        elif opcode.type == "do":
            code = "\tdo "
        # If opcode is of type while_do then generate while for do-while statement
        elif opcode.type == "while_do":
            code = "\twhile(%s);" % opcode.val
        # If opcode is of type if then generate if statement
        elif opcode.type == "if":
            code = "\tif(%s) " % opcode.val
        # If opcode is of type exit then generate exit statement
        elif opcode.type == "exit":
            code = "\texit(%s);\n" % opcode.val
        # If opcode is of type else_if then generate else if statement
        elif opcode.type == "else_if":
            code = "\telse if(%s) " % opcode.val
        # If opcode is of type else then generate else statement
        elif opcode.type == "else":
            code = "\telse "
        # If opcode is of type return then generate return statement
        elif opcode.type == "return":
            code += "\n\treturn " + opcode.val + ";\n"
            has_returned = True
        # If opcode is of type break then generate break statement
        elif opcode.type == "break":
            code += "\tbreak;\n"
        # If opcode is of type continue then generate continue statement
        elif opcode.type == "continue":
            code += "\tcontinue;\n"
        # If opcode is of type single_line_comment the generate single comment line
        elif opcode.type == "single_line_comment":
            code += "\t// %s \n" % opcode.val
        # If opcode is of type multi_line_comment the generate single comment line
        elif opcode.type == "multi_line_comment":
            code += "/* %s*/\n" % opcode.val
        # If opcode is of type switch then generate switch statement
        elif opcode.type == "switch":
            code += "\tswitch(" + opcode.val + ") "
        # If opcode is of type case then generate case statement
        elif opcode.type == "case":
            code += "\tcase " + opcode.val + ":\n"
        # If opcode is of type default then generate default statement
        elif opcode.type == "default":
            code += "\tdefault:\n"
        # If opcode is of type RAW_c, simpaly copy the value
        elif opcode.type == "raw":
            code += opcode.val + "\n"

        outside_code, ccode = compile_func_main_code(
            outside_code, ccode, outside_main, code
        )

    # Add return 0 to the end of code
    compiled_code += outside_code + ccode

    # Write generated code into C file
    with open(c_filename, "w") as file:
        file.write(compiled_code)
