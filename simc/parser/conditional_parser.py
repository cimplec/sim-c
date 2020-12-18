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
    from .simc_parser import expression

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

    ret_idx = i
    if(tokens[i].type == "newline"):
        ret_idx = i + 1
    if(tokens[i + 1].type == "left_brace"):
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
    from .simc_parser import expression

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

    if tokens[i + 1].type == "newline":
        i += 1
        while tokens[i].type == "newline":
            i += 1
        i -= 1

    check_if(
        tokens[i + 1].type,
        "left_brace",
        "Expected { after switch statement",
        tokens[i + 1].line_num,
    )

    return OpCode("switch", op_value[1:-1], ""), i, func_ret_type


def case_statement(tokens, i, table, func_ret_type):
    from .simc_parser import expression

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