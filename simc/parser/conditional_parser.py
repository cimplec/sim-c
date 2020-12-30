from ..global_helpers import error, check_if

from ..op_code import OpCode


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
    from .simc_parser import expression, skip_all_nextlines

    # Check if ( follows if statement
    check_if(
        got_type=tokens[i].type,
        should_be_types="left_paren",
        error_msg="Expected ( after if statement",
        line_num=tokens[i].line_num,
    )

    # check if expression follows ( in if statement
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside if statement",
        func_ret_type=func_ret_type,
    )

    # check if ) follows expression in if statement
    check_if(
        got_type=tokens[i - 1].type,
        should_be_types="right_paren",
        error_msg="Expected ) after expression in if statement",
        line_num=tokens[i - 1].line_num,
    )

    # If \n follows ) then skip all the \n characters
    if tokens[i + 1].type == "newline":
        i = skip_all_nextlines(tokens, i)
        i -= 1

    # Token index to be returned
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

    return OpCode("if", op_value[1:-1]), ret_idx - 1, func_ret_type


def switch_statement(tokens, i, table, func_ret_type):
    from .simc_parser import expression, skip_all_nextlines

    # Check if ( is present after switch keyword
    check_if(
        got_type=tokens[i].type, should_be_types="left_paren", 
        error_msg="Expected ( after switch", line_num=tokens[i].line_num
    )

    # Expected expression after ( in switch
    op_value, _, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside switch statement",
        func_ret_type=func_ret_type,
    )

    # Check if ) is present after expression in switch
    check_if(
        got_type=tokens[i - 1].type,
        should_be_types="right_paren",
        error_msg="Expected ) after expression in switch",
        line_num=tokens[i - 1].line_num,
    )

    # Skip all next lines before {
    if tokens[i + 1].type == "newline":
        i = skip_all_nextlines(tokens, i)
        i -= 1

    # Check if opening { is present, as switch cannot be single line
    check_if(
        got_type=tokens[i + 1].type,
        should_be_types="left_brace",
        error_msg="Expected { after switch statement",
        line_num=tokens[i + 1].line_num,
    )

    return OpCode("switch", op_value[1:-1], ""), i, func_ret_type


def case_statement(tokens, i, table, func_ret_type):
    from .simc_parser import expression

    # Expected expression after case keyword
    op_value, _, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expected expression after case",
        expect_paren=False,
        func_ret_type=func_ret_type,
    )

    # Check if expression is followed by : (colon) in case statement
    check_if(
        got_type=tokens[i].type,
        should_be_types="colon",
        error_msg="Expected : after case in switch statement",
        line_num=tokens[i].line_num,
    )

    return OpCode("case", op_value, ""), i + 1, func_ret_type
