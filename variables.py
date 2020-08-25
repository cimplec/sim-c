# Module to import some helper functions
from global_helpers import error

# Module to import parser helper functions
from parser_helpers import check_if, expression, check_ptr

# Module to import OpCode class
from op_code import OpCode


def var_statement(tokens, i, table, func_ret_type):
    """
    Parse variable declaration [/initialization] statement

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
    # Check if variable is also initialized
    if i + 1 < len(tokens) and tokens[i + 1].type == "assignment":
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

        # Map datatype to appropriate datatype in C
        prec_to_type = {
            0: "string",
            1: "string",
            2: "char",
            3: "int",
            4: "float",
            5: "double",
        }

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
