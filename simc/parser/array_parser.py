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

            error_message = "Array Initializer parsed incorrectly"
            op_value_temp, op_type, i_temp, func_ret_type = expression( tokens, i, table, error_message, flag=True )
            op_value += op_value_temp
            
            # If the size of the array is defined, and if the number of tokens parsed is not equal to 
            # what it should be, then display error
            if size_of_array != '' and (i_temp - i != int(size_of_array)+1) and tokens[i_temp-1].type != "comma":
                error( error_message, i )
            
            i = i_temp-1

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
