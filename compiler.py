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
    if(outside_main):
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

    # Loop through all opcodes
    for opcode in opcodes:
        code = ""
        # If opcode is of type print then generate a printf statement
        if opcode.type == "print":
            code = "\tprintf(%s);\n" % opcode.val
        # If opcode is of type var_assign then generate a declaration [/initialization] statement
        elif opcode.type == "var_assign":
            code = ""

            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            # Get the datatye of the variable
            _, dtype, _ = table.get_by_id(table.get_by_symbol(val[0]))

             #Helper Dictionaries
            get_data_type = {'i':"int", 's':"char*", 'f':"float", 'd':"double"}
            get_placeholder = {'i' : 'd', 's' : 's', 'f' : 'f', 'd' : 'lf'}

            # If it is of string type then change it to char <identifier>[]
            if(dtype == 'string'):
                dtype = 'char*'
            #Check if the statement is of type input or not
            if (len(val)<3):
                code += "\t" + dtype + " " + str(val[0]) + " = " + str(val[1]) + ";\n"
            else:
                #If the statement is of type input -
                dtype = get_data_type[val[2]]
                placeholder = get_placeholder[val[2]]
                code += "\t" + dtype +" "+ str(val[0])+ ";\n"
                code += "\t" + 'printf("' + str(val[1]) + '");\n'
                code += "\t" + 'scanf("%'+placeholder
                if ('*' in dtype ):
                    code += '", '+str(val[0])+');\n'
                else :
                    code += '", &'+str(val[0])+');\n'

        # If opcode is of type var_no_assign then generate a declaration statement
        elif opcode.type == "var_no_assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            # Get the datatye of the variable
            _, dtype, _ = table.get_by_id(table.get_by_symbol(val[0]))
            # Check if dtype could be inferred or not
            opcode.dtype = str(dtype) if dtype is not None else "not_known"

            code += "\t" + opcode.dtype + " " + str(opcode.val) + ";\n"
        # If opcode is of type assign then generate an assignment statement
        elif opcode.type == "assign":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            #Helper Dictionaries
            get_data_type = {'i':"int", 's':"char *", 'f':"float", 'd':"double"}
            get_placeholder = {'i' : 'd', 's' : 's', 'f' : 'f', 'd' : 'lf'}

            #Check if the statement is of type input or not
            if (len(val)<3):
                code += "\t" + val[0] + " = " + val[1] + ";\n"

            else:
                #If the statement is of type input -
                dtype = get_data_type[val[2]]
                placeholder = get_placeholder[val[2]]
                code += "\t" + 'printf("' + str(val[1]) + '");\n'
                code += "\t" + 'scanf("%'+placeholder+'", &'+str(val[0])+');\n'

            code += "\t" + val[0] + val[1] + ";\n"
        # If opcode is of type unary then generate an uanry statement
        elif opcode.type == "unary":
            # val contains - <identifier>---<expression>, split that into a list
            val = opcode.val.split('---')

            code += "\t" + opcode.val + ";\n"
        # If opcode is of type func_decl then generate function declaration statement
        elif opcode.type == "func_decl":
            # val contains - <identifier>---<params>, split that into list
            val = opcode.val.split('---')

            # Check if function has params
            params = val[1].split('&&&') if len(val[1]) > 0 else []

            # Get the return type of the function
            _, dtype, _ = table.get_by_id(table.get_by_symbol(val[0]))
            dtype = dtype if dtype is not "var" else "void"

            # Append the function return type and name to code
            code += "\n" + dtype + " " + val[0] + "("

            # Compile the formal params
            has_param = False
            for i in range(len(params)):
                if(len(params[i]) > 0):
                    has_param = True
                    _, dtype, _ = table.get_by_id(table.get_by_symbol(params[i]))
                    dtype = dtype if dtype is not "var" else "not_known"
                    code += dtype + " " + params[i] + ", "
            if(has_param):
                code = code[:-2]

            # Finally add opening brace to start the function body
            code += ") {\n"
        # If the opcode is of type func_call then generate function calling statement
        elif opcode.type == "func_call":
            # val contains - <identifier>---<params>, split that into list
            val = opcode.val.split('---')

            # Check if function has params
            params = val[1].split('&&&') if len(val[1]) > 0 else []

            # Compile function name
            code = "\t" + val[0] + "("

            # Compile the actual params
            has_param = False
            for param in params:
                if(len(params[i]) > 0):
                    has_param = True
                    code += param + ", "
            if(has_param):
                code = code[:-2]

            # Finally add opening brace to start the function body
            code += ");\n"
        # If opcode is of type scope_over then generate closing brace statement
        elif opcode.type == "scope_over":
            code += "}\n"
        # If opcode is of type scope_over then generate closing brace statement
        elif opcode.type == "MAIN":
            code += "\nint main() {\n"
            outside_main = False
        # If opcode is of type scope_over then generate closing brace statement
        elif opcode.type == "END_MAIN":
            code += "\n\treturn 0;\n}"
            outside_code, ccode = compile_func_main_code(outside_code, ccode, outside_main, code)
            outside_main = True
            continue
        # If opcode is of type for
        elif opcode.type == "for":
            val = opcode.val.split('&&&')
            code += "\tfor( int " + val[0] + " = " + val[1] + " ; " + val[0] + " " + val[4] + " " + val[2] + " ; " + val[0] + val[3] + "=" + val[5] +"){\n"
        # If opcode is of type while then generate while loop statement
        elif opcode.type == "while":
            code = "\twhile(%s) {\n" % opcode.val
        # If opcode is of type if then generate if statement
        elif opcode.type == "if":
            code = "\tif(%s) {\n" % opcode.val
        # If opcode is of type else_if then generate else if statement
        elif opcode.type == "else_if":
            code = "\telse if(%s) {\n" % opcode.val
        # If opcode is of type else then generate else statement
        elif opcode.type == "else":
            code = "\telse {\n"
        # If opcode is of type return then generate return statement
        elif opcode.type == "return":
            code += "\n\treturn " + opcode.val + ";\n"
        # If opcode is of type break then generate break statement
        elif opcode.type == "break":
            code += "\tbreak;\n"
        # If opcode is of type continue then generate continue statement
        elif opcode.type == "continue":
            code += "\tcontinue;\n"
        # If opcode is of type do_while then generate do while loop statement
        elif opcode.type == "do_while":
            do_scope = True
            code = "\tdo { \n " 

        outside_code, ccode = compile_func_main_code(outside_code, ccode, outside_main, code)

    # Add return 0 to the end of code
    compiled_code += outside_code + ccode

    # Write generated code into C file
    with open(c_filename, "w") as file:
        file.write(compiled_code)
