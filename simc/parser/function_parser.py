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

    # Store the beginning index for function call from imported libraries
    beg_idx = i

    # Get information about the function from symbol table
    func_info = table.get_by_id(tokens[i].val)
    func_name = func_info[0]
    metadata = func_info[2]

    # Get all parameter ids (default and non-default) and the default values (if any)
    params, default_values = extract_func_typedata(metadata, table)
    num_formal_params = len(params)
    num_required_args = num_formal_params - len(default_values)
    
    # Parse the arguments
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i + 1,
        table,
        "",
        accept_empty_expression=True,
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
    if num_actual_params != num_required_args:
        error(
            "Expected {} arguments but got {} in function {}".format(
                num_required_args, num_actual_params, func_name
            ),
            tokens[i].line_num,
        )

    # Fill the missing values in function call with default values
    op_value_list = fill_missing_args_with_defaults(
        op_value_list, default_values, num_actual_params, num_formal_params
    )
    # Assign datatype to formal parameters
    for j in range(len(params)):
        # If parameter list is empty
        if params[j] == ")":
            continue

        # Fetch the datatype of corresponding actual parameter from symbol table
        _, dtype, _, _ = table.get_by_id(
            table.get_by_symbol(op_value_list[j].replace(")", ""))
        )

        param_id = table.get_by_symbol(params[j])

        # Set the datatype of the formal parameter
        table.symbol_table[param_id][1] = dtype

        # Resolve pendenting infer types
        table.resolve_dependency(tokens, i, param_id)

    use_module_tokens = False

    # If it an imported function the type of the function will be a list containing tokens from module's lexing results
    # Push all the function names and the corresponding position from where to parse
    if func_info != -1 and type(func_info[1][2]) == list:
        func_ret_type = {func_name: func_info[1][1]}
        use_module_tokens = True

    # Handles delayed inference of return types, this can occur in two situations 
    # 1 - When the function is part of third party module, 2 - When the function's parameter are contained in return expression
    if func_name in func_ret_type.keys():
        # Case 1
        if use_module_tokens:
            # Parse the tokens which will help in deciding on the return type
            _, op_type, _, _ = expression(
                func_info[1][2], func_ret_type[func_name], table, ""
            )

        # Case 2
        else:
            _, op_type, _, _ = expression(tokens, func_ret_type[func_name], table, "")

        #  Map datatype to appropriate datatype in C
        prec_to_type = {
            -1: "declared",
            0: "char*",
            1: "char*",
            2: "char",
            3: "int",
            4: "float",
            5: "double",
            6: "bool",
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

    func_typedata_split = typedata.split("&&&")

    param_segment = func_typedata_split[0]

    # Ignore the first index as it contains function's name
    parameters = param_segment.split("---")[1:]

    default_values = []
    for seg in func_typedata_split[1:]:
        default_value, _, _, _ = table.get_by_id(int(seg))
        default_values.append(default_value)

    return parameters, default_values


def fill_missing_args_with_defaults(
    op_value_list, default_values, num_actual_params, num_formal_params
):

    # Compute the offset of default values according to the missing values count
    offset = len(default_values) - num_formal_params + num_actual_params
    default_values = default_values[offset:]

    # If there are not default values to be filled
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

    from .simc_parser import skip_all_nextlines

    # Check if identifier follows fun
    check_if(got_type=tokens[i].type, should_be_types="id", 
             error_msg="Expected function name", line_num=tokens[i].line_num)

    # Store the id of function name in symbol table
    func_idx = tokens[i].val

    # Get function name
    func_name, _, _, _ = table.get_by_id(func_idx)

    # Check if ( follows id in function
    check_if(
        got_type=tokens[i + 1].type,
        should_be_types="left_paren",
        error_msg="Expected ( after function name",
        line_num=tokens[i + 1].line_num,
    )

    # Get the function parameter [and default value] tuples
    parameters, i = function_parameters(tokens, i + 2, table)

    # Check if ) follows expression in function
    check_if(
        got_type=tokens[i - 1].type,
        should_be_types="right_paren",
        error_msg="Expected ) after function params list",
        line_num=tokens[i - 1].line_num,
    )

    # If \n follows ) then skip all the \n characters
    if tokens[i + 1].type == "newline":
        i = skip_all_nextlines(tokens, i)
        i -= 1

    op_codes = []

    # Index to be returned to main parsing loop
    ret_idx = i

    if tokens[i].type == "newline":
        ret_idx = i + 1

    if tokens[i + 1].type == "left_brace":
        # Loop until } is reached
        i += 1
        ret_idx = i
        found_right_brace = False

        while i < len(tokens) and tokens[i].type != "right_brace":
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
    parameter_names = [parameter[0] for parameter in parameters]
    default_values = [str(parameter[1]) for parameter in parameters if parameter[1] is not None]

    func_typedata = "function"
    if parameter_names:
        func_typedata += "---" + "---".join(parameter_names)
    if default_values:
        func_typedata += "&&&" + "&&&".join(default_values)

    table.symbol_table[func_idx][2] = func_typedata

    op_codes.append(
        OpCode("func_decl", func_name + "---" + "&&&".join(parameter_names), "")
    )

    # The order now is scope_begin followed by func_decl, but the compiler expects the opposite order
    op_codes.reverse()

    return (
        op_codes,
        ret_idx - 1,
        func_name,
        func_ret_type,
    )


def function_parameters(tokens, i, table):
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

        return [], i

    parameters = []
    default_val_required = False

    # Get the first parameter [and default value]
    param_info, i = function_parameter(tokens, i, table, default_val_required)

    # If there are parameters
    if param_info is not None:

        parameters.append(param_info)
        _, default_val = param_info
        default_val_required = default_val is not None

        # Continue parsing until comma tokens are encountered
        while tokens[i].type == "comma":
            # Skip comma token
            i += 1

            # Get parameter [and default value]
            param_info, i = function_parameter(tokens, i, table, default_val_required)

            if param_info is not None:
                parameters.append(param_info)
                if not default_val_required:
                    _, default_val = param_info
                    default_val_required = default_val is not None
            else:
                error("Parameter expected after comma", tokens[i].line_num)

        check_if(
            got_type=tokens[i].type,
            should_be_types="right_paren",
            error_msg="Right parentheses expected",
            line_num=tokens[i].line_num,
        )

        # Skip right parantheses
        i += 1

    else:
        error("Function parameters must be identifiers", tokens[i].line_num)

    return parameters, i


def function_parameter(tokens, i, table, default_val_required):
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

    # Get the parameter from symbol table id stored in token
    parameter, _, _, _ = table.get_by_id(tokens[i].val)
    i += 1

    default_val = None

    # To handle the case when a parameter on left has default value and the current one does not
    if default_val_required:
        check_if(
            got_type=tokens[i].type,
            should_be_types="assignment",
            error_msg="Default value expected for parameter {}".format(parameter),
            line_num=tokens[i].line_num,
        )

        # Skip the assignment operator
        i += 1

        # Default parameter values can be number or string only as of now
        if tokens[i].type in ["number", "string"]:
            default_val = tokens[i].val
            i += 1
        else:
            error(
                "Only numbers and strings are allowed as default arguments",
                tokens[i].line_num,
            )
    elif tokens[i].type == "assignment":
        i += 1
        if tokens[i].type in ["number", "string"]:
            default_val = tokens[i].val
            i += 1
        else:
            error(
                "Only numbers and strings are allowed as default arguments",
                tokens[i].line_num,
            )

    return (parameter, default_val), i
