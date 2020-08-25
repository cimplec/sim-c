# Module to import some helper functions
from global_helpers import error

# Module to import parser helper functions
from parser_helpers import check_if, expression

# Module to import OpCode class
from op_code import OpCode


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
    check_if(
        tokens[i + 2].type, "number", "Expected starting value", tokens[i + 2].line_num
    )

    # Check if to keyword follows number
    check_if(tokens[i + 3].type, "to", "Expected to keyword", tokens[i + 3].line_num)

    # Check if number follows in keyword
    check_if(
        tokens[i + 4].type, "number", "Expected ending value", tokens[i + 4].line_num
    )

    # Check if by keyword follows number
    check_if(tokens[i + 5].type, "by", "Expected by keyword", tokens[i + 5].line_num)

    word_to_op = {"plus": "+", "minus": "-", "multiply": "*", "divide": "/"}

    # Check if number follows operator
    check_if(
        tokens[i + 7].type,
        "number",
        "Expected value for change",
        tokens[i + 7].line_num,
    )

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
        i + 1,
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
        i += 2
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

        return OpCode("while", op_value[:-1]), ret_idx - 1, func_ret_type
    else:
        return OpCode("while_do", op_value[:-1]), i + 1, func_ret_type
