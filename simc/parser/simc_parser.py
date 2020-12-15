# Module to import some helper functions
from ..global_helpers import error, check_if

# Module to import OpCode class
from ..op_code import OpCode

# Import various parsing functions
from .function_parser import function_call_statement, function_definition_statement
from .array_parser import array_initializer
from .loop_parser import for_statement, while_statement
from .conditional_parser import if_statement, switch_statement, case_statement
from .variable_parser import var_statement, assign_statement
from .struct_parser import struct_declaration_statement

# Import parser constants
from .parser_constants import OP_TOKENS, WORD_TO_OP

def expression(
    tokens,
    i,
    table,
    msg,
    accept_unkown=False,
    accept_empty_expression=False,
    expect_paren=True,
    func_ret_type={},
):
    """
    Parse and expression from tokens
    Params
    ======
    tokens                  (list)        = List of tokens
    i                       (string/list) = Current index in list of tokens
    table                   (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    msg                     (string)      = Error message to print in case some case fails
    accept_unkown           (bool)        = Accept unknown type for variable or not
    accept_empty_expression (bool)        = Accept empty expression or not
    expect_paren            (bool)        = Expect parenthesis at the end
    func_ret_type           (string)      = Functions return type
    Returns
    =======
    string, string, int: The expression, datatype of the expression and the current index in source
                         code after parsing
    """
    # Initial values
    op_value = ""
    op_type = -1

    # Mapping for precedence checking (double > float > int)
    type_to_prec = {"int": 3, "float": 4, "double": 5}

    #Mapping simc constant name to c constant name
    math_constants = {"PI":"M_PI", "E":"M_E" , "inf":"INFINITY", "NaN":"NAN"}

    # count parentheses
    count_paren = 0

    # Loop until expression is not parsed completely
    while i < len(tokens) and tokens[i].type in OP_TOKENS:
        # Check for function call
        if tokens[i].type == "id" and tokens[i + 1].type == "left_paren":
            fun_opcode, i, func_ret_type = function_call_statement(
                tokens, i, table, func_ret_type
            )
            val = fun_opcode.val.split("---")
            params = val[1].split("&&&")
            op_value += val[0] + "(" + ", ".join(params) + ")"
            type_to_prec = {"char*": 1, "char": 2, "int": 3, "float": 4, "double": 5}
            op_type = type_to_prec[table.get_by_id(table.get_by_symbol(val[0]))[1]]
            i -= 1
        # If token is identifier or constant
        elif tokens[i].type in ["number", "string", "id"]:
            # Fetch information from symbol table
            value, type, typedata = table.get_by_id(tokens[i].val)

            if type == "string" or type == "char*":
                # If { in string then it is a f-string
                if "{" in value:
                    vars = []
                    temp_var = ""
                    enter = False

                    # Collect the variable names
                    for char in value:
                        if char == "{":
                            enter = True
                        elif char == "}":
                            vars.append(temp_var[1:])
                            temp_var = ""
                            enter = False

                        if enter:
                            temp_var += char

                    # Determine the type of variables and append the name of variables at the end
                    type_to_fs = {
                        "char": "%c",
                        "char*": "%s",
                        "string": "%s",
                        "int": "%d",
                        "float": "%f",
                        "double": "%lf",
                    }
                    for var in vars:
                        _, type, _ = table.get_by_id(table.get_by_symbol(var))
                        if type == "var":
                            error("Unknown variable %s" % var, tokens[i].line_num)
                        value = value.replace('{'+var+'}', type_to_fs[type])
                        value += ", " + var

                    # Replace all {} in string
                    value = value.replace("{", "").replace("}", "")
                op_value += value
                op_type = 0 if typedata == "constant" else 1
            elif type == "char":
                op_value += value
                op_type = 2
            elif type == "int":
                op_value += str(value)
                op_type = (
                    type_to_prec["int"] if type_to_prec["int"] > op_type else op_type
                )
            elif type == "float":
                op_value += str(value)
                op_type = (
                    type_to_prec["float"]
                    if type_to_prec["float"] > op_type
                    else op_type
                )
            elif type == "double":
                op_value += math_constants.get(str(value),str(value))
                op_type = (
                    type_to_prec["double"]
                    if type_to_prec["double"] > op_type
                    else op_type
                )
            elif type in ["var", "declared"] and not accept_unkown:
                error("Cannot find the type of %s" % value, tokens[i].line_num)
            elif type == "var" and accept_unkown:
                op_value += str(value)
        elif tokens[i].type in ["newline", "call_end"]:
            break
        else:
            if tokens[i].type == "power":
                # Fetch information from symbol table for first operand
                value_first, _, _ = table.get_by_id(tokens[i-1].val)

                # Fetch information from symbol table for second operand (exponent)
                value_second, _, _ = table.get_by_id(tokens[i+1].val)

                # Remove the operand from before pow()
                op_value = op_value[:-(len(value_first))]
                op_value += f"pow({value_first}, {value_second})"

                i += 1
            elif tokens[i].type == "left_paren":
                count_paren += 1
                op_value += WORD_TO_OP[tokens[i].type]
            elif tokens[i].type == "right_paren":
                count_paren -= 1

                if count_paren < 0:
                    error("Found unexpected ‘)’ in expression", tokens[i].line_num)
                op_value += WORD_TO_OP[tokens[i].type]
            else:
                op_value += WORD_TO_OP[tokens[i].type]

        i += 1

    if count_paren > 0:
        error("Expected ‘)’ before end of expression", tokens[i].line_num)

    # If expression is empty then throw an error
    if op_value == "" and not accept_empty_expression:
        error(msg, tokens[i].line_num)

    # Check if statement is of type input
    if " scanf " in op_value:

        # Check if there exists a prompt message
        if '"' in op_value:
            i1 = op_value.index('"') + 1
            i2 = op_value.index('"', i1)
            # Extracting the prompt
            p_msg = op_value[i1:i2]
            # Checking if dtype is mentioned
            if "'" in op_value[i2 + 1 :]:
                i1 = op_value.index("'", i2 + 1) + 1
                i2 = op_value.index("'", i1)
                dtype = op_value[i1:i2]
            else:
                # default dtype is string
                dtype = "s"
        else:
            p_msg = ""
            dtype = "s"
        dtype_to_prec = {"i": 3, "f": 4, "d": 5, "s": 1, "c": 2}
        op_value = str(p_msg) + "---" + str(dtype)
        op_type = dtype_to_prec[dtype]
    # Return the expression, type of expression, and current index in source codes
    return op_value, op_type, i, func_ret_type

def print_statement(tokens, i, table, func_ret_type):
    """
    Parse print statement
    Params
    ======
    tokens        (list)        = List of tokens
    i             (int)         = Current index in token
    table         (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    func_ret_type (string)      = Function return type
    Returns
    =======
    OpCode, int: The opcode for the print code and the index after parsing print statement
    Grammar
    =======
    print_statement -> print(expr)
    expr            -> string | number | id | operator
    string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote           -> "
    number          -> [0-9]+
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> + | - | * | /
    """

    # Check if ( follows print statement
    check_if(
        tokens[i].type,
        "left_paren",
        "Expected ( after print statement",
        tokens[i].line_num,
    )

    # Check if expression follows ( in print statement
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside print statement",
        func_ret_type=func_ret_type,
    )

    # Map datatype to appropriate format specifiers
    prec_to_type = {
        0: "",
        1: '"%s", ',
        2: '"%c", ',
        3: '"%d", ',
        4: '"%f", ',
        5: '"%lf", ',
    }
    op_value = prec_to_type[op_type] + op_value[1:-1]

    # Check if print statement has closing )
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in print statement",
        tokens[i - 1].line_num,
    )

    # Return the opcode and i+1 (the token after print statement)
    return OpCode("print", op_value), i + 1, func_ret_type

def unary_statement(tokens, i, table, func_ret_type):
    """
    Parse unary statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    OpCode, int: The opcode for the unary code and the index after parsing unary statement
    Grammar
    =======
    unary_statement -> id operator
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> ++ | --
    """

    # Check if assignment operator follows identifier name
    if tokens[i].type not in ["increment", "decrement"]:
        check_if(
            tokens[i + 1].type,
            ["increment", "decrement"],
            "Expected unary operator after identifier",
            tokens[i + 1].line_num,
        )
        # Check if expression follows = in assign statement
        op_value, _, i, func_ret_type = expression(
            tokens,
            i,
            table,
            "",
            accept_empty_expression=True,
            expect_paren=False,
            func_ret_type=func_ret_type,
        )
        # Return the opcode and i (the token after unary statement)
        return OpCode("unary", op_value), i, func_ret_type

    else:
        check_if(
            tokens[i + 1].type,
            "id",
            "Expected identifier after unary operator",
            tokens[i + 1].line_num,
        )
        op_value = -1
        if tokens[i].type == "increment":
            op_value = "++ --- "
        else:
            op_value = "-- --- "
        value, func_ret_type, _ = table.get_by_id(tokens[i + 1].val)
        op_value += str(value)
        return OpCode("unary", op_value), i + 2, func_ret_type


def exit_statement(tokens, i, table, func_ret_type):
    """
    Parse exit statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    OpCode, int: The opcode for the assign code and the index after parsing exit statement
    Grammar
    =======
    exit_statement -> exit(expr)
    expr            -> number
    number          -> [0-9]+
    """
    # Check if ( follows exit statement
    check_if(
        tokens[i].type,
        "left_paren",
        "Expected ( after exit statement",
        tokens[i].line_num,
    )

    # Check if number follows ( in exit statement
    check_if(
        tokens[i + 1].type,
        "number",
        "Expected number after ( in exit statement",
        tokens[i].line_num,
    )

    # check if expression follows ( in exit statement
    op_value, _, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside exit statement",
        func_ret_type=func_ret_type,
    )
    op_value_list = op_value.replace(" ", "").split(",")
    # check if ) follows expression in exit statement
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in exit statement",
        tokens[i - 1].line_num,
    )

    return OpCode("exit", op_value[1:-1]), i, func_ret_type


def parse(tokens, table):
    """
    Parse tokens and generate opcodes
    Params
    ======
    tokens (list) = List of tokens
    Returns
    =======
    list: The list of opcodes
    Grammar
    =======
    statement -> print_statement | var_statement | assign_statement | function_definition_statement
    """

    # List of opcodes
    op_codes = []

    # Current function's name
    func_name = ""

    # Do while started or not
    in_do = False

    # Count main functions
    main_fn_count = 0

    # Count if conditions
    if_count = 0

    # Brace count
    brace_count = 0

    # If function return type could not be figured out during return then do it while calling
    func_ret_type = {}

    # If a struct is declared, make this variable true, then if its true add a semicolon after the next right parenthesis
    struct_declared = -1

    # Loop through all the tokens
    i = 0

    while i <= len(tokens) - 1:

        # If token is raw c type
        if tokens[i].type == "RAW_C":
            op_codes.append(OpCode("raw",tokens[i].val))
            i += 1
            continue


        # If token is of type print then generate print opcode
        if tokens[i].type == "print":
            print_opcode, i, func_ret_type = print_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(print_opcode)
        # If token is of type import then generate import opcode
        elif tokens[i].type == "import":
            i += 1
            check_if(tokens[i].type, "id", "Expected module name after import", tokens[i].line_num)
            value, _, _ = table.get_by_id(tokens[i].val)
            op_codes.append(OpCode("import", value))
            i += 1
        # If token is of type var then generate var opcode
        elif tokens[i].type == "var":
            var_opcode, i, func_ret_type = var_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(var_opcode)
        # If token is of type id then generate assign opcode
        elif tokens[i].type == "id":
            # If '(' follows id then it is function calling else variable assignment
            if tokens[i + 1].type == "left_paren":
                fun_opcode, i, func_ret_type = function_call_statement(
                    tokens, i, table, func_ret_type
                )
                op_codes.append(fun_opcode)
            elif tokens[i + 1].type in ["increment", "decrement"]:
                unary_opcode, i, func_ret_type = unary_statement(
                    tokens, i, table, func_ret_type
                )
                op_codes.append(unary_opcode)
            elif tokens[i+1].type in ["to","by"] or tokens[i-2].type =='by':
                i+=1
            else:
                assign_opcode, i, func_ret_type = assign_statement(
                    tokens, i + 1, table, func_ret_type
                )
                op_codes.append(assign_opcode)
        # If token is of type fun then generate function opcode
        elif tokens[i].type == "fun":
            fun_opcode, i, func_name, func_ret_type = function_definition_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(fun_opcode)
        # If token is of type struct then generate structure opcode
        elif tokens[i].type == "struct":
            struct_opcode, i, struct_name = struct_declaration_statement(
                tokens, i + 1, table
            )
            struct_declared = brace_count
            op_codes.append(struct_opcode)
        # If token is of type left_brace then generate scope_begin opcode
        elif tokens[i].type == "left_brace":
            op_codes.append(OpCode("scope_begin", "", ""))
            brace_count += 1
            i += 1
        # If token is of type right_brace then generate scope_over opcode, if a struct was declared earlier, generate struct_scope_over opcode
        elif tokens[i].type == "right_brace":
            brace_count -= 1
            if struct_declared == brace_count:
                # instance_name stores the name of structure instance (seperated by commas if multiple instances), if defined
                instance_names = ""
                # loop through the subsequent tokens to find all instantiated objects
                for j in range(i+1, len(tokens)):
                    if tokens[j].type == "id":
                        instance_names += table.get_by_id(tokens[j].val)[0] + ", "
                        # Skip over the id type token
                        i += 1
                    elif tokens[j].type == "comma":
                        i += 1
                        continue
                    else:
                        break
                op_codes.append(OpCode("struct_scope_over", instance_names[:-2], ""))
                struct_declared = -1

            else:
                op_codes.append(OpCode("scope_over", "", ""))
            

            if brace_count < 0:
                error(
                    "Closing brace doesn't match any previous opening brace",
                    tokens[i].line_num,
                )
            i += 1

            if brace_count == 0:
                # The Function scope is over
                func_name = ""
                
        # If token is of type MAIN then generate MAIN opcode
        elif tokens[i].type == "MAIN":
            op_codes.append(OpCode("MAIN", "", ""))
            main_fn_count += 1
            if main_fn_count > 1:
                error("Presence of two MAIN in a single file", tokens[i].line_num)
            i += 1
        # If token is of type END_MAIN then generate MAIN opcode
        elif tokens[i].type == "END_MAIN":
            op_codes.append(OpCode("END_MAIN", "", ""))
            main_fn_count -= 1
            i += 1
        # If token is of type for then generate for code
        elif tokens[i].type == "for":
            for_opcode, i, func_ret_type = for_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(for_opcode)
        # If token is of type do then generate do_while code
        elif tokens[i].type == "do":
            
            # If \n follows ) then skip all the \n characters
            if tokens[i + 1].type == "newline":
                i += 1
                while tokens[i].type == "newline":
                    i += 1
                i -= 1
            
            check_if(
                tokens[i + 1].type,
                "left_brace",
                "Expected { after do statement",
                tokens[i + 1].line_num,
            )
            in_do = True
            op_codes.append(OpCode("do", "", ""))
            i += 1
        # If token is of type while then generate while opcode
        elif tokens[i].type == "while":
            while_opcode, i, func_ret_type = while_statement(
                tokens, i + 1, table, in_do, func_ret_type
            )
            if in_do:
                in_do = False
            op_codes.append(while_opcode)
        # If token is of type if then generate if opcode
        elif tokens[i].type == "if":
            if_opcode, i, func_ret_type = if_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(if_opcode)
            # Increment if count on encountering if
            if_count += 1
        # If token is of type exit then generate exit opcode
        elif tokens[i].type == "exit":
            exit_opcode, i, func_ret_type = exit_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(exit_opcode)
        # If token is of type else then check whether it is else if or else
        elif tokens[i].type == "else":
            
            # If \n follows else then skip all the \n characters
            if tokens[i + 1].type == "newline":
                i += 1
                while tokens[i].type == "newline":
                    i += 1
                i -= 1
                
            # If the next token is if, then it is else if
            if tokens[i + 1].type == "if":
                if_opcode, i, func_ret_type = if_statement(
                    tokens, i + 2, table, func_ret_type
                )
                if_opcode.type = "else_if"
                op_codes.append(if_opcode)
            # Otherwise it is else
            elif tokens[i + 1].type == "left_brace":
                op_codes.append(OpCode("else", "", ""))

                # Decrement if count on encountering if, to make sure there aren't extra else conditions
                if_count -= 1

                # If if_count is negative then the current else is extra
                if if_count < 0:
                    error("Else does not match any if!", tokens[i].line_num)

                i += 1
        # If token is of type return then generate return opcode
        elif tokens[i].type == "return":
            beg_idx = i + 1
            if tokens[i + 1].type not in ["id", "number", "string", "left_paren"]:
                op_value = ""
                op_type = 6
                i += 1
            else:
                op_value, op_type, i, func_ret_type = expression(
                    tokens,
                    i + 1,
                    table,
                    "Expected expression after return",
                    True,
                    True,
                    expect_paren=False,
                    func_ret_type=func_ret_type,
                )

            if func_name == "" and main_fn_count == 0:
                error("Return statement outside any function", tokens[i].line_num)
            else:
                #  Map datatype to appropriate datatype in C
                prec_to_type = {
                    -1: "not_known",
                    0: "char*",
                    1: "char*",
                    2: "char",
                    3: "int",
                    4: "float",
                    5: "double",
                    6: "void",
                }

                # If we are in main function, 
                # the default return is going to be generated anyways, so skip this
                if main_fn_count == 0:
                    # We are not in main function
                    if op_type == -1:
                        func_ret_type[func_name] = beg_idx
                    # Change return type of function
                    if op_type != -1:
                        table.symbol_table[table.get_by_symbol(func_name)][1] = prec_to_type[
                            op_type
                        ]
                    else:
                        table.symbol_table[table.get_by_symbol(func_name)][1] = [prec_to_type[op_type], beg_idx, tokens]

            op_codes.append(OpCode("return", op_value, ""))
        # If token is of type break then generate break opcode
        elif tokens[i].type == "break":
            op_codes.append(OpCode("break", "", ""))
            i += 1
        # If token is of type continue then generate continue opcode
        elif tokens[i].type == "continue":
            op_codes.append(OpCode("continue", "", ""))
            i += 1
        # If token is of type single_line_statement then generate single_line_comment opcode
        elif tokens[i].type == "single_line_comment":
            op_codes.append(OpCode("single_line_comment", tokens[i].val, ""))
            i += 1
        # If token is of type multi_line_statement then generate multi_line_comment opcode
        elif tokens[i].type == "multi_line_comment":
            op_codes.append(OpCode("multi_line_comment", tokens[i].val, ""))
            i += 1
        # If token is of type switch then generate switch opcode
        elif tokens[i].type == "switch":
            switch_opcode, i, func_ret_type = switch_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(switch_opcode)
        # If token is of type case then generate case opcode
        elif tokens[i].type == "case":
            case_opcode, i, func_ret_type = case_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(case_opcode)
        # If token is of type default then generate default opcode
        elif tokens[i].type == "default":
            check_if(
                tokens[i + 1].type,
                "colon",
                "Expected : after default statement in switch",
                tokens[i + 1].line_num,
            )
            op_codes.append(OpCode("default", "", ""))
            i += 2
        # If token is the type increment or decrement then generate unary_opcode
        elif tokens[i].type in ["increment", "decrement"]:
            unary_opcode, i, func_ret_type = unary_statement(
                tokens, i, table, func_ret_type
            )
            op_codes.append(unary_opcode)

        # Otherwise increment the index
        else:
            i += 1

    # Errors that may occur after parsing loop
    if main_fn_count > 0:
        error("No matching END_MAIN for MAIN", tokens[i - 1].line_num + 1)
    elif main_fn_count < 0:
        error("No matching MAIN for END_MAIN", tokens[i-1].line_num + 1)

    # Return opcodes
    return op_codes
