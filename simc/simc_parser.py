# Module to import some helper functions
from .global_helpers import error

# Module to import OpCode class
from .op_code import OpCode


def check_if(given_type, should_be_types, msg, line_num):
    """
    Check if type matches what it should be otherwise throw an error and exit
    Params
    ======
    given_type      (string)      = Type of token to be checked
    should_be_types (string/list) = Type(s) to be compared with
    msg             (string)      = Error message to print in case some case fails
    line_num        (int)         = Line number
    """

    # Convert to list if type is string
    if type(should_be_types) == str:
        should_be_types = [should_be_types]

    # If the given_type is not part of should_be_types then throw error and exit
    if given_type not in should_be_types:
        error(msg, line_num)


def function_call_statement(tokens, i, table, func_ret_type):
    """
    Parse function calling statement
    Params
    ======
    tokens        (list)        = List of tokens
    i             (int)         = Current index in token
    table         (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    func_ret_type (dict)        = If return type of function is not figured yet
    Returns
    =======
    OpCode, int, dict: The opcode for the assign code, index after parsing function calling statement and function return type
    Grammar
    =======
    function_call_statement   -> id([actual_params,]*)
    actual_params             -> expr
    body                      -> statement
    expr                      -> string | number | id | operator
    string                    -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote                     -> "
    number                    -> [0-9]+
    id                        -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator                  -> + | - | * | /
    """

    # Get information about the function from symbol table
    func_name, _, metadata = table.get_by_id(tokens[i].val)

    params, default_values = extract_func_typedata(metadata, table)
    num_formal_params = len(params)
    num_required_args = num_formal_params - len(default_values)

    # Parse the arguments
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i + 1,
        table,
        "",
        True,
        True,
        expect_paren=True,
        func_ret_type=func_ret_type,
    )
    # op_value start in 1 because it should start with "params)" not "(params)"
    op_value = op_value[1:]
    op_value_list = op_value.replace(" ", "").split(",")
    op_value_list = (
        op_value_list if len(op_value_list) > 0 and len(op_value_list[0]) > 0 else []
    )
    num_actual_params = len(op_value_list) if op_value_list != [")"] else 0

    # Check if number of actual and formal parameters match
    if num_actual_params < num_required_args:
        error(
            "Expected at least %d arguments but got %d in function %s".format(
                num_required_args, num_actual_params, func_name
            ),
            tokens[i].line_num
        )

    if num_actual_params > num_formal_params:
        error(
            "Expected not more than %d arguments but got %d in function %s".format(
                num_formal_params, num_actual_params, func_name
            ),
            tokens[i].line_num
        )

    op_value_list = fill_missing_args_with_defaults(
        op_value_list,
        default_values,
        num_actual_params,
        num_formal_params
    )

    # Assign datatype to formal parameters
    for j in range(len(params)):
        # If parameter list is empty
        if params[j] == ")":
            continue

        # Fetch the datatype of corresponding actual parameter from symbol table
        _, dtype, _ = table.get_by_id(
            table.get_by_symbol(op_value_list[j].replace(")", ""))
        )

        # Set the datatype of the formal parameter
        table.symbol_table[table.get_by_symbol(params[j])][1] = dtype

    if func_name in func_ret_type.keys():
        _, op_type, _, _ = expression(tokens, func_ret_type[func_name], table, "")

        #  Map datatype to appropriate datatype in C
        prec_to_type = {
            0: "char*",
            1: "char*",
            2: "char",
            3: "int",
            4: "float",
            5: "double",
        }

        table.symbol_table[table.get_by_symbol(func_name)][1] = prec_to_type[op_type]
        del func_ret_type[func_name]

    return (
        OpCode("func_call", func_name + "---" + "&&&".join(op_value_list)[:-1], ""),
        i + 1,
        func_ret_type,
    )


def extract_func_typedata(typedata, table):
    """
    Extract typedata of function
    Params
    ======
    typedata    (string)        = Typedata of function in format "function---param1---param2---...&&&default_val1&&&...
    table       (SymbolTable)   = Symbol table
    Returns
    =======
    parameters      (list)  = Parameter names
    default_values  (list)  = Default values
    """
    segments = typedata.split("&&&")
    param_segment = segments[0]
    parameters = param_segment.split("---")[1:]
    default_values = []
    for seg in segments[1:]:
        default_value, _, _ = table.get_by_id(int(seg))
        default_values.append(default_value)

    return parameters, default_values


def fill_missing_args_with_defaults(
        op_value_list,
        default_values,
        num_actual_params,
        num_formal_params):

    offset = len(default_values) - num_formal_params + num_actual_params
    default_values = default_values[offset:]

    if not default_values:
        return op_value_list

    args = []
    for op_value in op_value_list:
        arg = op_value.replace(")", "")
        if arg:
            args.append(arg)
    args += default_values
    args[-1] = args[-1] + ")"

    return args


def function_definition_statement(tokens, i, table, func_ret_type):
    """
    Parse function definition statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    func_ret_type (string) = Function return type
    Returns
    =======
    OpCode, int, string: The opcode for the assign code, the index, and the name of the function after
                         parsing function calling statement
    Grammar
    =======
    function_definition_statement   -> fun id([formal_param,]*) { body }
    formal_params                   -> id ('=' default_value)
    default_value                   -> number || string
    body                            -> statement
    id                              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    """

    # Check if identifier follows fun
    check_if(tokens[i].type, "id", "Expected function name", tokens[i].line_num)

    # Store the id of function name in symbol table
    func_idx = tokens[i].val

    # Get function name
    func_name, _, _ = table.get_by_id(func_idx)

    # Check if ( follows id in function
    check_if(
        tokens[i + 1].type,
        "left_paren",
        "Expected ( after function name",
        tokens[i + 1].line_num,
    )

    parameters, i = function_parameters(tokens, i + 2, table)

    # Check if ) follows expression in function
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after function params list",
        tokens[i - 1].line_num,
    )

    # If \n follows ) then skip all the \n characters
    if tokens[i + 1].type == "newline":
        i += 1
        while tokens[i].type == "newline":
            i += 1
        i -= 1

    # Check if { follows ) in function
    check_if(
        tokens[i + 1].type,
        "left_brace",
        "Expected { before function body",
        tokens[i + 1].line_num,
    )

    # Loop until } is reached
    i += 2
    ret_idx = i
    found_right_brace = False
    while i < len(tokens) and tokens[i].type != "right_brace":
        if tokens[i].type == "right_brace":
            found_right_brace = True
        i += 1

    # If right brace found at end
    if i != len(tokens) and tokens[i].type == "right_brace":
        found_right_brace = True

    # If right brace is not found then produce error
    if not found_right_brace:
        error("Expected } after function body", tokens[i].line_num)

    # Add the identifier types to function's typedata
    parameter_names = [p[0] for p in parameters]
    default_values = [str(p[1]) for p in parameters if p[1] is not None]
    func_typedata = "function"
    if parameter_names:
        func_typedata += "---" + "---".join(parameter_names)
    if default_values:
        func_typedata += "&&&" + "&&&".join(default_values)
    table.symbol_table[func_idx][2] = func_typedata

    return (
        OpCode("func_decl", func_name + "---" + "&&&".join(parameter_names), ""),
        ret_idx - 1,
        func_name,
        func_ret_type,
    )


def function_parameters(
        tokens,
        i,
        table):
    """
    Parse function parameters
    Params
    ======
    tokens  (list)          = List of tokens
    i       (int)           = Current index in list of tokens
    table   (SymbolTable)   = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    parameters  (list)  = List of parameters (= list of (ids, default))
    i           (int)   = Current index in list of tokens
    """
    if tokens[i].type == "right_paren":

        i += 1

        # check_if(tokens[i].type,
        #          "call_end",
        #          "End of call expected",
        #          tokens[i].line_num)

        return [], i

    parameters = []
    default_val_required = False

    param_info, i = function_parameter(tokens,
                                       i,
                                       table,
                                       default_val_required)
    if param_info is not None:

        parameters.append(param_info)
        _, default_val = param_info
        default_val_required = default_val is not None

        while tokens[i].type == "comma":
            i += 1
            param_info, i = function_parameter(tokens,
                                               i,
                                               table,
                                               default_val_required)
            if param_info is not None:
                parameters.append(param_info)
                if not default_val_required:
                    _, default_val = param_info
                    default_val_required = default_val is not None
            else:
                error("Parameter expected after comma", tokens[i].line_num)

        check_if(tokens[i].type,
                 "right_paren",
                 "Right parentheses expected",
                 tokens[i].line_num)
        i += 1

        # check_if(tokens[i].type,
        #          "call_end",
        #          "End of call expected",
        #          tokens[i].line_num)

    else:
        error("Function parameters must be identifiers",
              tokens[i].line_num)

    return parameters, i


def function_parameter(
        tokens,
        i,
        table,
        default_val_required):
    """
    Parse function parameter
    Params
    ======
    tokens  (list)              = List of tokens
    i       (int)               = Current index in list of tokens
    table   (SymbolTable)       = Symbol table constructed holding information about identifiers and constants
    default_val_required (bool) = Default value is required
    Returns
    =======
    (parameter, default_val_id?)    (tuple?) = Parameter and optional default value id or none
    i                               (int)    = Current index in list of tokens
    """
    if tokens[i].type != "id":
        return None, i

    parameter, _, _ = table.get_by_id(tokens[i].val)
    i += 1

    default_val = None

    if default_val_required:
        check_if(tokens[i].type,
                 "assignment",
                 "Default value expected for parameter {}".format(parameter),
                 tokens[i].line_num)
        i += 1
        if tokens[i].type in ["number", "string"]:
            default_val = tokens[i].val
            i += 1
        else:
            error("Only numbers and strings are allowed as default arguments",
                  tokens[i].line_num)
    elif tokens[i].type == "assignment":
        i += 1
        if tokens[i].type in ["number", "string"]:
            default_val = tokens[i].val
            i += 1
        else:
            error("Only numbers and strings are allowed as default arguments",
                  tokens[i].line_num)

    return (parameter, default_val), i


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
    while i < len(tokens) and tokens[i].type in [
        "number",
        "input",
        "string",
        "id",
        "plus",
        "minus",
        "multiply",
        "power",
        "divide",
        "comma",
        "equal",
        "not_equal",
        "greater_than",
        "less_than",
        "greater_than_equal",
        "less_than_equal",
        "modulus",
        "increment",
        "decrement",
        "plus_equal",
        "minus_equal",
        "multiply_equal",
        "divide_equal",
        "modulus_equal",
        "power_equal",
        "and",
        "or",
        "left_paren",
        "exit",
        "right_paren",
        "newline",
        "call_end",
        "address_of",
        "right_shift",
        "left_shift",
    ]:
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

            if type == "string":
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
                        "string": "%s",
                        "int": "%d",
                        "float": "%f",
                        "double": "%lf",
                    }
                    for var in vars:
                        _, type, _ = table.get_by_id(table.get_by_symbol(var))
                        if type == "var":
                            error("Unknown variable %s" % var, tokens[i].line_num)
                        value = value.replace(var, type_to_fs[type])
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
            word_to_op = {
                "plus": " + ",
                "minus": " - ",
                "multiply": " * ",
                "divide": " / ",
                " comma ": ", ",
                "equal": " == ",
                "not_equal": " != ",
                "greater_than": " > ",
                "less_than": " < ",
                "greater_than_equal": " >= ",
                "less_than_equal": " <= ",
                "input": " scanf ",
                "modulus": " % ",
                "increment": " ++ ",
                "decrement": " -- ",
                "plus_equal": " += ",
                "minus_equal": " -= ",
                "multiply_equal": " *= ",
                "divide_equal": " /= ",
                "modulus_equal": " %= ",
                "and": " && ",
                "or": " || ",
                "comma": ",",
                "left_paren": "(",
                "right_paren": ")",
                "address_of": "&",
                "left_shift": " << ",
                "right_shift": " >> ",
                "power": ""
            }

            # if (
            #     expect_paren
            #     and tokens[i].type == "right_paren"
            #     and tokens[i + 1].type in ["newline", "left_brace"]
            # ):
            #     break

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
                # if(tokens[i-1].type != "id"):
                count_paren += 1;
                op_value += word_to_op[tokens[i].type]
            elif tokens[i].type == "right_paren":
                count_paren -= 1;

                if count_paren < 0:
                    error("Found unexpected ‘)’ in expression", tokens[i].line_num)
                op_value += word_to_op[tokens[i].type]
            else:
                op_value += word_to_op[tokens[i].type]

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
        dtype_to_prec = {"i": 3, "f": 4, "d": 5, "s": 1}
        op_value = str(p_msg) + "---" + str(dtype)
        op_type = dtype_to_prec[dtype]
    # Return the expression, type of expression, and current index in source codes
    return op_value, op_type, i, func_ret_type


def check_ptr(tokens, i):
    # Check if a pointer is being declared
    is_ptr = False
    # Count the depth of pointer
    count_ast = 0
    if tokens[i].type == "multiply":
        j = 0
        while tokens[i + j].type == "multiply":
            j += 1
        i += j
        count_ast = j
        is_ptr = True
        return is_ptr, count_ast, i
    else:
        return False, 0, i


def for_statement(tokens, i, table, func_ret_type):
    """
    Parse for for_loop
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    OpCode, int: The opcode for the for loop code and the index after parsing for loop
    Grammar
    =======
    for_loop    -> for id in number to number by operator number
    number      -> [0-9]+
    id          -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator    -> + | - | * | /
    """

    # Check if identifier follows for keyword
    check_if(tokens[i].type, "id", "Expected variable name", tokens[i].line_num)

    # Check if in follows identifier
    check_if(tokens[i + 1].type, "in", "Expected in keyword", tokens[i + 1].line_num)

    # Check if number follows in keyword
    expression(tokens,i+2,table,"Expected starting value",expect_paren=False)

    # Check if to keyword follows number
    check_if(tokens[i + 3].type, "to", "Expected to keyword", tokens[i + 3].line_num)

    # Check if number follows in keyword
    expression(tokens,i+4,table,"Expected ending value",expect_paren=False)
    
    # Check if by keyword follows number
    check_if(tokens[i + 5].type, "by", "Expected by keyword", tokens[i + 5].line_num)

    word_to_op = {"plus": "+", "minus": "-", "multiply": "*", "divide": "/"}

    # Check if number follows operator
    expression(tokens,i+7,table,"Expected value for change",expect_paren=False)
    
    # Get required values
    var_name, _, _ = table.get_by_id(tokens[i].val)
    table.symbol_table[tokens[i].val][1] = "int"
    starting_val, _, _ = table.get_by_id(tokens[i + 2].val)
    ending_val, _, _ = table.get_by_id(tokens[i + 4].val)
    operator_type = word_to_op[tokens[i + 6].type]
    change_val, _, _ = table.get_by_id(tokens[i + 7].val)

    # To determine the > or < sign
    if starting_val > ending_val:
        sign_needed = ">"
    else:
        sign_needed = "<"

    # Return the opcode and i+1 (the token after for loop statement)
    return (
        OpCode(
            "for",
            str(var_name)
            + "&&&"
            + str(starting_val)
            + "&&&"
            + str(ending_val)
            + "&&&"
            + str(operator_type)
            + "&&&"
            + sign_needed
            + "&&&"
            + str(change_val),
        ),
        i + 1,
        func_ret_type,
    )


def while_statement(tokens, i, table, in_do, func_ret_type):
    """
    Parse while statement
    Params
    ======
    tokens      (list)        = List of tokens
    i           (int)         = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    in_do       (bool)        = While is part of do-while or is a separate while
    Returns
    =======
    OpCode, int: The opcode for the assign code and the index after parsing while statement
    Grammar
    =======
    while_statement -> while(condition) { body }
    condition       -> expr
    expr            -> string | number | id | operator
    string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote           -> "
    number          -> [0-9]+
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> + | - | * | /
    """
    # Check if ( follows while statement
    check_if(
        tokens[i].type,
        "left_paren",
        "Expected ( after while statement",
        tokens[i].line_num,
    )

    # check if expression follows ( in while statement
    op_value, _, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside while statement",
        func_ret_type=func_ret_type,
    )

    # check if ) follows expression in while statement
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in while statement",
        tokens[i - 1].line_num,
    )

    # If while is not part of do-while
    if not in_do:
        # If \n follows ) then skip all the \n characters
        if tokens[i + 1].type == "newline":
            i += 1
            while tokens[i].type == "newline":
                i += 1
            i -= 1

        # Check if { follows ) in while statement
        check_if(
            tokens[i + 1].type,
            "left_brace",
            "Expected { before while loop body",
            tokens[i + 1].line_num,
        )

        # Loop until } is reached
        i += 1
        ret_idx = i
        found_right_brace = False
        while i < len(tokens) and tokens[i].type != "right_brace":
            if found_right_brace:
                found_right_brace = True
            i += 1

        # If right brace found at end
        if i != len(tokens) and tokens[i].type == "right_brace":
            found_right_brace = True

        # If right brace is not found then produce error
        if not found_right_brace:
            error("Expected } after while loop body", tokens[i].line_num)

        return OpCode("while", op_value[1:-1]), ret_idx - 1, func_ret_type
    else:
        return OpCode("while_do", op_value[1:-1]), i + 1, func_ret_type


def if_statement(tokens, i, table, func_ret_type):
    """
    Parse if statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    OpCode, int: The opcode for the assign code and the index after parsing if statement
    Grammar
    =======
    if_statement -> if(condition) { body }
    condition       -> expr
    expr            -> string | number | id | operator
    string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote           -> "
    number          -> [0-9]+
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> + | - | * | /
    """
    # Check if ( follows if statement
    check_if(
        tokens[i].type,
        "left_paren",
        "Expected ( after if statement",
        tokens[i].line_num,
    )

    # check if expression follows ( in if statement
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside if statement",
        func_ret_type=func_ret_type,
    )
    op_value_list = op_value.replace(" ", "").split(",")
    # check if ) follows expression in if statement
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in if statement",
        tokens[i - 1].line_num,
    )

    # If \n follows ) then skip all the \n characters
    if tokens[i + 1].type == "newline":
        i += 1
        while tokens[i].type == "newline":
            i += 1
        i -= 1

    # Check if { follows ) in if statement
    check_if(
        tokens[i + 1].type,
        "left_brace",
        "Expected { before if body",
        tokens[i + 1].line_num,
    )

    # Loop until } is reached
    i += 1
    ret_idx = i 
    found_right_brace = False
    while i < len(tokens) and tokens[i].type != "right_brace":
        if found_right_brace:
            found_right_brace = True
        i += 1

    # If right brace found at end
    if i != len(tokens) and tokens[i].type == "right_brace":
        found_right_brace = True

    return OpCode("if", op_value[1:-1]), ret_idx - 1, func_ret_type


def switch_statement(tokens, i, table, func_ret_type):

    check_if(
        tokens[i].type, "left_paren", "Expected ( after switch", tokens[i].line_num
    )

    op_value, _, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside switch statement",
        func_ret_type=func_ret_type,
    )

    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in switch",
        tokens[i - 1].line_num,
    )

    check_if(
        tokens[i + 1].type,
        "left_brace",
        "Expected { after switch statement",
        tokens[i + 1].line_num,
    )

    return OpCode("switch", op_value[1:-1], ""), i, func_ret_type


def case_statement(tokens, i, table, func_ret_type):

    op_value, _, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expected expression after case",
        expect_paren=False,
        func_ret_type=func_ret_type,
    )

    check_if(
        tokens[i].type,
        "colon",
        "Expected : after case in switch statement",
        tokens[i].line_num,
    )

    return OpCode("case", op_value, ""), i + 1, func_ret_type


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


def var_statement(tokens, i, table, func_ret_type):
    """
    Parse variable and array declaration [/initialization] statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    func_ret_type (string) = Function return type
    Returns
    =======
    OpCode, int: The opcode for the var_assign/var_no_assign code and the index after parsing var statement
    Grammar
    =======
    var_statement   -> var id [= expr]?
    expr            -> string | number | id | operator
    string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote           -> "
    number          -> [0-9]+
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> + | - | * | /
    """

    is_ptr, count_ast, i = check_ptr(tokens, i)
    # Check if identifier is present after var
    check_if(tokens[i].type, "id", "Expected id after var keyword", tokens[i].line_num)

    # Tokens that are not accepted after declaration of a variable
    invalid_tokens = [
        "plus_equal",
        "minus_equal",
        "divide_equal",
        "multiply_equal",
        "plus",
        "minus",
        "divide",
        "multiply",
        "modulus",
        "modulus_equal",
        "equal",
        "not_equal",
    ]

    # Map datatype to appropriate datatype in C
    prec_to_type = {
        0: "string",
        1: "char*",
        2: "char",
        3: "int",
        4: "float",
        5: "double",
    }

    # Check if it is a array initializer
    if tokens[i + 1].type == "left_bracket":
        
        # Number of position allocated in array
        num_field_expec = ''
        
        # Store the index of identifier
        id_idx = i

        # Fetch information from symbol table
        value, type, _ = table.get_by_id(tokens[i + 2].val)

        # Expect the number be integer
        if type == "int":
            num_field_expec = value

            # Check if array statement has closing ] (right_bracket)
            check_if(
                tokens[i + 3].type,
                "right_bracket",
                "Expected ] after expression in array statement",
                tokens[i + 3].line_num,
            )
            # Position indice to end of array declaration (right bracket)
            i += 3
        elif tokens[i + 2].type == "right_bracket":
            # Define max array length
            num_field_expec =  ''
            # Position indice to end of array declaration (right bracket)
            i += 2
        else:
            error("Expected integer number after expression in array statement", tokens[i + 2].line_num)  

        # Check if array is also initialized
        if i + 1 < len(tokens) and tokens[i + 1].type == "assignment":
            
            # Check if expression follows = in array statement
            op_value, op_type, i = array_initializer(
                tokens,
                i + 2,
                table,
                num_field_expec,
                "Required expression after assignment operator",
            )

            # Modify datatype of the identifier
            table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]

            # Return the opcode and i (the token after var statement)
            return (
                OpCode(
                    "array_assign",
                    table.symbol_table[tokens[id_idx].val][0] + "---" + str(num_field_expec) + "---" + op_value,
                    prec_to_type[op_type],
                ),
                i,
                op_type,
            )
        elif i + 1 < len(tokens) and tokens[i + 1].type in invalid_tokens:
            error("Invalid Syntax for declaration", tokens[i].line_num)
        else:
            # Get the value from symbol table by id
            value, type, _ = table.get_by_id(tokens[id_idx].val)

            # If already declared then throw error
            if type in [
                "declared",
                "int",
                "char",
                "float",
                "double",
                "string",
                "char *",
                "char*",
            ]:
                error("Variable %s already declared" % value, tokens[i].line_num)

            # Set declared
            table.symbol_table[tokens[id_idx].val][1] = "declared"

            return (OpCode("array_no_assign", value + "---" + str(num_field_expec)), i, func_ret_type)
            
    # Check if variable is also initialized
    elif i + 1 < len(tokens) and tokens[i + 1].type == "assignment":
        # Store the index of identifier
        id_idx = i

        # Check if expression follows = in var statement
        op_value, op_type, i, func_ret_type = expression(
            tokens,
            i + 2,
            table,
            "Required expression after assignment operator",
            expect_paren=False,
            func_ret_type=func_ret_type,
        )

        # Modify datatype of the identifier
        table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]

        if is_ptr:
            return (
                OpCode(
                    "ptr_assign",
                    table.symbol_table[tokens[id_idx].val][0]
                    + "---"
                    + op_value
                    + "---"
                    + str(count_ast),
                    prec_to_type[op_type],
                ),
                i,
                func_ret_type,
            )
        else:
            # Return the opcode and i (the token after var statement)
            return (
                OpCode(
                    "var_assign",
                    table.symbol_table[tokens[id_idx].val][0] + "---" + op_value,
                    prec_to_type[op_type],
                ),
                i,
                func_ret_type,
            )
    elif i + 1 < len(tokens) and tokens[i + 1].type in invalid_tokens:
        error("Invalid Syntax for declaration", tokens[i].line_num)
    else:
        # Get the value from symbol table by id
        value, type, _ = table.get_by_id(tokens[i].val)

        # If already declared then throw error
        if type in [
            "declared",
            "int",
            "char",
            "float",
            "double",
            "string",
            "char *",
            "char*",
        ]:
            error("Variable %s already declared" % value, tokens[i].line_num)

        # Set declared
        table.symbol_table[tokens[i].val][1] = "declared"

        # Return the opcode and i+1 (the token after var statement)
        if is_ptr:
            return OpCode("ptr_no_assign", value), i + 1, func_ret_type

        return OpCode("var_no_assign", value), i + 1, func_ret_type

def assign_statement(tokens, i, table, func_ret_type):
    """
    Parse assignment statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    OpCode, int: The opcode for the assign code and the index after parsing assign statement
    Grammar
    =======
    var_statement   -> var id [= expr]?
    expr            -> string | number | id | operator
    string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote           -> "
    number          -> [0-9]+
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> + | - | * | /
    """

    # Check if the identifier is a pointer
    is_ptr = False
    # count depth of pointer
    count_ast = 0
    if tokens[i - 2].type == "multiply":
        j = -2
        while tokens[j + i].type == "multiply":
            j -= 1
        count_ast = -1 * j - 2
        is_ptr = True

    # Check if variable is declared or not
    value, type, _ = table.get_by_id(tokens[i - 1].val)

    if type == "var":
        error("Variable %s used before declaration" % value, tokens[i - 1].line_num)

    # Dictionary to convert tokens to their corresponding assignment types
    assignment_type = {
        "assignment": "=",
        "plus_equal": "+=",
        "minus_equal": "-=",
        "multiply_equal": "*=",
        "divide_equal": "/=",
        "modulus_equal": "%=",
    }
    # Check if assignment operator follows identifier name
    check_if(
        tokens[i].type,
        [
            "assignment",
            "plus_equal",
            "minus_equal",
            "multiply_equal",
            "divide_equal",
            "modulus_equal",
        ],
        "Expected assignment operator after identifier",
        tokens[i].line_num,
    )
    # Convert the token to respective symbol
    converted_type = assignment_type[tokens[i].type]
    # Store the index of identifier
    id_idx = i - 1

    # Check if expression follows = in assign statement
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i + 1,
        table,
        "Required expression after assignment operator",
        expect_paren=False,
        func_ret_type=func_ret_type,
    )
    #  Map datatype to appropriate datatype in C
    prec_to_type = {
        0: "string",
        1: "string",
        2: "char",
        3: "int",
        4: "float",
        5: "double",
    }
    op_value = converted_type + "---" + op_value
    # Modify datatype of the identifier
    table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]
    # Check if a pointer is being assigned
    if is_ptr:
        return (
            OpCode(
                "ptr_only_assign",
                table.symbol_table[tokens[id_idx].val][0]
                + "---"
                + op_value
                + "---"
                + str(count_ast),
                "",
            ),
            i,
            func_ret_type,
        )

    # Return the opcode and i (the token after assign statement)
    return (
        OpCode(
            "assign", table.symbol_table[tokens[id_idx].val][0] + "---" + op_value, ""
        ),
        i,
        func_ret_type,
    )


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
        # If token is of type left_brace then generate scope_begin opcode
        elif tokens[i].type == "left_brace":
            op_codes.append(OpCode("scope_begin", "", ""))
            brace_count += 1
            i += 1
        # If token is of type right_brace then generate scope_over opcode
        elif tokens[i].type == "right_brace":
            op_codes.append(OpCode("scope_over", "", ""))
            brace_count -= 1

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
                    table.symbol_table[table.get_by_symbol(func_name)][1] = prec_to_type[
                        op_type
                    ]

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