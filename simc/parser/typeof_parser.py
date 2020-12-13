from ..global_helpers import error, check_if

from ..op_code import OpCode

def typeof_statement(tokens, i, table, func_ret_type):
    """
    Parse typeof statement
    Params
    ======
    tokens        (list)        = List of tokens
    i             (int)         = Current index in token
    table         (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    func_ret_type (string)      = Function return type
    Returns
    =======
    OpCode, int: The opcode for the typeof code and the index after parsing typeof statement
    Grammar
    =======
    typeof_statement -> typeof(id)
    expr            -> string | number | id | operator
    string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
    quote           -> "
    number          -> [0-9]+
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> + | - | * | /
    """

    from .simc_parser import expression

    # Check if ( follows typeof statement
    check_if(
        tokens[i].type,
        "left_paren",
        "Expected ( after typeof statement",
        tokens[i].line_num,
    )    

    # Check if expression follows ( in typeof statement
    op_value, op_type, i, func_ret_type = expression(
        tokens,
        i,
        table,
        "Expected expression inside typeof statement",
        func_ret_type=func_ret_type,
    )
    op_value = op_value[1:-1]
    _, op_value, op_type = table.get_by_id(table.get_by_symbol(op_value))
    if (not op_type == "variable"):
        error("typeof operator expects a variable as argument")

    # _, dtype, _ = table.get_by_id()
    # op_value = '"%s"' % dtype
    # Check if typeof statement has closing )
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in typeof statement",
        tokens[i - 1].line_num,
    )
    # Return the opcode and i+1 (the token after typeof statement)
    return OpCode("typeof", op_value), i + 1, func_ret_type