from ..global_helpers import error, check_if

from ..op_code import OpCode

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

    from .simc_parser import expression

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
            "Expected at least {} arguments but got {} in function {}".format(
                num_required_args, num_actual_params, func_name
            ),
            tokens[i].line_num
        )

    if num_actual_params > num_formal_params:
        error(
            "Expected not more than {} arguments but got {} in function {}".format(
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

    func_token_val = table.symbol_table.get(table.get_by_symbol(func_name), -1)
    use_module_tokens = False
    if func_token_val != -1 and type(func_token_val[1][2]) == list:
        func_ret_type = {func_name: func_token_val[1][1]}
        use_module_tokens = True

    if func_name in func_ret_type.keys():
        if use_module_tokens:
            _, op_type, _, _ = expression(func_token_val[1][2], func_ret_type[func_name], table, "")
        else:
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
    OpCodes, int, string: The opcodes for the assign code, the index, and the name of the function after
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

    op_codes = []

    ret_idx = i
    if tokens[i].type == "newline":
        ret_idx = i + 1
    if tokens[i + 1].type == "left_brace":
        # Loop until } is reached
        i += 1
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

    else:
        op_codes.append(OpCode("scope_begin", "", ""))

    # Add the identifier types to function's typedata
    parameter_names = [p[0] for p in parameters]
    default_values = [str(p[1]) for p in parameters if p[1] is not None]
    func_typedata = "function"
    if parameter_names:
        func_typedata += "---" + "---".join(parameter_names)
    if default_values:
        func_typedata += "&&&" + "&&&".join(default_values)
    table.symbol_table[func_idx][2] = func_typedata

    op_codes.append(OpCode("func_decl", func_name + "---" + "&&&".join(parameter_names), ""))
    op_codes.reverse()
    return (
        op_codes,
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