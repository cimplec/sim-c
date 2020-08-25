# Module to import some helper functions
from global_helpers import error

# Module to import parser helper functions
from parser_helpers import check_if, expression

# Module to import OpCode class
from op_code import OpCode


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
        i + 1,
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
    op_value = prec_to_type[op_type] + op_value[:-1]

    # Check if print statement has closing )
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in print statement",
        tokens[i - 1].line_num,
    )

    # Return the opcode and i+1 (the token after print statement)
    return OpCode("print", op_value), i + 1, func_ret_type
