from .global_helpers import error, check_if

from .op_code import OpCode

def array_initializer(
    tokens, 
    i,
    table,
    num_field_expec,
    msg
):
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

    # Initial values
    op_value = ""
    op_type = -1

    # Mapping for precedence checking (double > float > int)
    type_to_prec = {"int": 3, "float": 4, "double": 5}

    #Mapping simc constant name to c constant name
    math_constants = {"PI":"M_PI", "E":"M_E" , "inf":"INFINITY", "NaN":"NAN"}
    
    # Count values
    count_values = 0

    # type predicted
    typed = ""

    # Mark if comma if need
    expected_comma = False 

    # Check if identifier follows for keyword
    check_if(tokens[i].type, "left_brace", "Expected  {", tokens[i].line_num)
    op_value += "{"

    max_length_array = 2**32 
   
    if num_field_expec != '':
        max_length_array = int(num_field_expec)

    # Loop until values expected or expression is not correctly
    while i < len(tokens)-1:
        
        # Check end  of expression, stop loop
        if(tokens[i].type == "right_brace"):
            op_value += "}"
            break
        
        # The values overflow size of declared array
        if(count_values > max_length_array):
            error("Too many initializers ", tokens[i].line_num)    

        # If is a new line, go to next
        if(tokens[i].type == "newline"):
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
            error("Expected values properly separed by comma", tokens[i].line_num);

            
        # If token is identifier or constant
        if tokens[i].type in ["number", "string", "id"]:
            # Fetch information from symbol table
            value, type, typedata = table.get_by_id(tokens[i].val)
      
            # Check if there is more than one type in initializers
            if(count_values > 1 and type != typed):
                error("Too many types in initializers", tokens[i].line_num)
            else:
                typed = type

            # Check for function call
            if tokens[i].type == "id" and tokens[i + 1].type == "left_paren":
                fun_opcode, i, _ = function_call_statement(
                    tokens, i, table, {}
                )
                val = fun_opcode.val.split("---")
                params = val[1].split("&&&")
                op_value += val[0] + "(" + ", ".join(params) + ")"
                type_to_prec = {"char*": 1, "char": 2, "int": 3, "float": 4, "double": 5}
                op_type = type_to_prec[table.get_by_id(table.get_by_symbol(val[0]))[1]]
                typed = type
                i -= 1
            # Process element assigned
            elif type == "string" and typedata == "constant":
                op_value += value
                op_type = 1
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
            elif type in ["var", "declared"]:
                error("Cannot find the type of %s" % value, tokens[i].line_num)

            # Expected comma 
            expected_comma = True
        count_values += 1
        i += 1

    # one comma after expression is allowed
    if tokens[i].type == "comma":
        i += 1

    # Check if identifier follows for keyword
    check_if(tokens[i].type, "right_brace", "Expected  }", tokens[i].line_num)

    return op_value, op_type, i + 1 