from ..global_helpers import error, check_if

from ..op_code import OpCode


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
    from .simc_parser import expression

    # Check if identifier follows for keyword
    check_if(got_type=tokens[i].type, should_be_types="id", 
             error_msg="Expected variable name", line_num=tokens[i].line_num)

    # Check if in follows identifier
    check_if(got_type=tokens[i + 1].type, should_be_types="in", 
             error_msg="Expected in keyword", line_num=tokens[i + 1].line_num)

    # Check if number follows in keyword
    expression(tokens, i + 2, table, "Expected starting value", expect_paren=False)

    # Check if to keyword follows number
    check_if(got_type=tokens[i + 3].type, should_be_types="to", 
             error_msg="Expected to keyword", line_num=tokens[i + 3].line_num)

    # Check if number follows in keyword
    expression(tokens, i + 4, table, "Expected ending value", expect_paren=False)

    # Check if by keyword follows number
    check_if(got_type=tokens[i + 5].type, should_be_types="by", 
             error_msg="Expected by keyword", line_num=tokens[i + 5].line_num)

    word_to_op = {"plus": "+", "minus": "-", "multiply": "*", "divide": "/"}

    # Check if number follows operator
    expression(tokens, i + 7, table, "Expected value for change", expect_paren=False)

    # Get required values
    var_name, _, _, _ = table.get_by_id(tokens[i].val)

    # Set the value
    table.symbol_table[tokens[i].val][1] = "int"

    starting_val, _, _, _ = table.get_by_id(tokens[i + 2].val)
    ending_val, _, _, _ = table.get_by_id(tokens[i + 4].val)
    operator_type = word_to_op[tokens[i + 6].type]
    change_val, _, _, _ = table.get_by_id(tokens[i + 7].val)

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
    from .simc_parser import expression, skip_all_nextlines

    # Check if ( follows while statement
    check_if(
        got_type=tokens[i].type,
        should_be_types="left_paren",
        error_msg="Expected ( after while statement",
        line_num=tokens[i].line_num,
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
        got_type=tokens[i - 1].type,
        should_be_types="right_paren",
        error_msg="Expected ) after expression in while statement",
        line_num=tokens[i - 1].line_num,
    )

    # If while is not part of do-while
    if not in_do:
        # If \n follows ) then skip all the \n characters
        if tokens[i + 1].type == "newline":
            i = skip_all_nextlines(tokens, i)
            i -= 1

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
                error("Expected } after while loop body", tokens[i].line_num)

        return OpCode("while", op_value[1:-1]), ret_idx - 1, func_ret_type
    else:
        return OpCode("while_do", op_value[1:-1]), i + 1, func_ret_type
