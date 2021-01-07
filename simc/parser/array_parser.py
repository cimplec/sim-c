from ..global_helpers import error, check_if

from ..op_code import OpCode


def array_initializer(tokens, i, table, size_of_array, msg):
    """
    Parse array assigment
    Params
    ======
    tokens                  (list)        = List of tokens
    i                       (string/list) = Current index in list of tokens
    table                   (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    num_field_expec         (number)      = Number of fileds expected to fill
    msg                     (string)      = Error message to print in case some case fails
    Returns
    =======
    string, string, int: The expression, datatype of the expression and the current index in source
                         code after parsing
    """
    from .simc_parser import expression
    from .function_parser import function_call_statement

    # Initial values
    op_value = ""
    op_type = -1

    # Mapping for precedence checking (double > float > int)
    type_to_prec = {"int": 3, "float": 4, "double": 5}

    # Mapping simc constant name to c constant name
    math_constants = {"PI": "M_PI", "E": "M_E", "inf": "INFINITY", "NaN": "NAN"}

    # Number of values initialized
    initialized_value_counts = 0

    # Predicted type of variable
    type_of_id = ""

    # Mark if comma if need
    expected_comma = False

    # Check if left brace follows assignment operator
    check_if(got_type=tokens[i].type, should_be_types="left_brace", 
             error_msg="Expected  {", line_num=tokens[i].line_num)

    # Begin array initializer
    op_value += "{"

    # Maximum possible length of array
    max_length_array = 2 ** 32

    # If size is not empty then update max_length_array to that size
    if size_of_array != "":
        max_length_array = int(size_of_array)

    # Loop until right brace
    while i < len(tokens) - 1:

        # Check end  of expression, stop loop
        if tokens[i].type == "right_brace":
            op_value += "}"
            break

        # The values overflow size of declared array
        if initialized_value_counts > max_length_array:
            error("Too many initializers ", tokens[i].line_num)

        # If is a new line, go to next
        if tokens[i].type == "newline":
            op_value += "\n"
            i += 1
            continue

        # Check for comma before next element
        if expected_comma and tokens[i].type == "comma":
            expected_comma = False
            op_value += ","
            i += 1
            continue
        elif expected_comma or (expected_comma is False and tokens[i].type == "comma"):
            error("Expected values to be separated by comma in initializer list", tokens[i].line_num)

        # If token is identifier or constant
        if tokens[i].type in ["number", "string", "id"]:
            # Fetch information from symbol table
            value, type_, typedata = table.get_by_id(tokens[i].val)

            # Check if there is more than one type in initializers
            if initialized_value_counts > 1 and type_ != type_of_id:
                error("Too many unique types in initializers", tokens[i].line_num)
            else:
                type_of_id = type_

            # Check for function call
            if tokens[i].type == "id" and tokens[i + 1].type == "left_paren":
                fun_opcode, i, _ = function_call_statement(
                    tokens, i, table, {}
                )

                # Function have opcode value of 
                # <func-name>---[<param-1>&&&<param-2>, ..., <param-n>]
                # Fetch infor from function's opcode
                func_info = fun_opcode.val.split("---")

                # Fetch the parameter names
                params = func_info[1].split("&&&")

                # Convert into format <func-name>([<param-1>, <param-2>, ..., <param-n>])
                op_value += func_info[0] + "(" + ", ".join(params) + ")"

                # Get return type of function from symbol table
                type_to_prec = {"char*": 1, "char": 2, "int": 3, "float": 4, "double": 5}
                op_type = type_to_prec[table.get_by_id(table.get_by_symbol(func_info[0]))[1]]

                # The element corresponding to the key op_type is assigned to type_of_id
                type_of_id = [k for k,v in type_to_prec.items() if v == op_type]
                type_of_id = type_of_id[0]

                i -= 1
            # Process element assigned
            elif type_ == "string" and typedata == "constant":
                op_value += value
                op_type = 1
            elif type_ == "char":
                op_value += value
                op_type = 2
            elif type_ == "int":
                op_value += str(value)
                op_type = (
                    type_to_prec["int"] if type_to_prec["int"] > op_type else op_type
                )
            elif type_ == "float":
                op_value += str(value)
                op_type = (
                    type_to_prec["float"]
                    if type_to_prec["float"] > op_type
                    else op_type
                )
            elif type_ == "double":
                op_value += math_constants.get(str(value), str(value))
                op_type = (
                    type_to_prec["double"]
                    if type_to_prec["double"] > op_type
                    else op_type
                )
            elif type_ in ["var", "declared"]:
                error("Cannot find the type of %s" % value, tokens[i].line_num)

            # Expected comma
            expected_comma = True

        initialized_value_counts += 1
        i += 1

    # one comma after expression is allowed
    if tokens[i].type == "comma":
        i += 1

    # Check if ending right brace is present or not
    check_if(got_type=tokens[i].type, should_be_types="right_brace", 
             error_msg="Expected  }", line_num=tokens[i].line_num)

    return op_value, op_type, i + 1
