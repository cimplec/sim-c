# Module to import some helper functions
from global_helpers import error

# Module to import parser helper functions
from parser_helpers import check_if, expression

# Module to import OpCode class
from op_code import OpCode


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

    # Extract params from functions metadata (typedata), these are stored as <id>---[<param 1>, . . . , <param n>]
    params = metadata.split("---")[1:] if "---" in metadata else [")"]

    # Parse the params
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i + 2,
        table,
        "",
        True,
        True,
        expect_paren=True,
        func_ret_type=func_ret_type,
    )
    op_value_list = op_value.replace(" ", "").split(",")
    op_value_list = (
        op_value_list if len(op_value_list) > 0 and len(op_value_list[0]) > 0 else []
    )

    # Check if number of actual and formal parameters match
    if len(params) != len(op_value_list):
        error(
            "Expected %d parameters but got %d parameters in function %s"
            % (len(params), len(op_value_list), func_name),
            tokens[i].line_num,
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
    function_definition_statement   -> fun id([formal_params,]*) { body }
    formal_params                   -> expr
    body                            -> statement
    expr                            -> string | number | id | operator
    string                          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote                           -> "
    number                          -> [0-9]+
    id                              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator                        -> + | - | * | /
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

    # Check if expression follows ( in function statement
    op_value, op_type, i, func_ret_type = expression(
        tokens, i + 2, table, "", True, True, func_ret_type=func_ret_type
    )
    op_value_list = op_value.replace(" ", "").replace(")", "").split(",")

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
    table.symbol_table[func_idx][2] = (
        "function---" + "---".join(op_value_list)
        if len(op_value_list) > 0 and len(op_value_list[0]) > 0
        else "function"
    )

    return (
        OpCode("func_decl", func_name + "---" + "&&&".join(op_value_list), ""),
        ret_idx - 1,
        func_name,
        func_ret_type,
    )
