from ..global_helpers import error, check_if, check_incomplete

from ..op_code import OpCode

def check_ptr(tokens, i):
    # Check if a pointer is being declared
    is_ptr = False
    # Count the depth of pointer
    count_ast = 0
    check_incomplete(
        i,
        tokens,
        "Improper Declaration",
        tokens[i-1].line_num,
    )
    if tokens[i].type == "multiply":
        j = 0
        while tokens[i + j].type == "multiply":
            j += 1
        i += j
        count_ast = j
        is_ptr = True
        return is_ptr, count_ast, i
    else:
        return False, 0, i

def var_statement(tokens, i, table, func_ret_type):
    """
    Parse variable and array declaration [/initialization] statement
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
    from .array_parser import array_initializer
    from .simc_parser import expression

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
        "bitwise_and",
        "bitwise_or",
        "bitwise_xor",
        "bitwise_and_equal",
        "bitwise_or_equal",
        "bitwise_xor_equal",
        "multiply",
        "modulus",
        "modulus_equal",
        "equal",
        "not_equal",
    ]

    # Map datatype to appropriate datatype in C
    prec_to_type = {
        0: "string",
        1: "char*",
        2: "char",
        3: "int",
        4: "float",
        5: "double",
    }

    # Check if it is a array initializer
    if tokens[i + 1].type == "left_bracket":
        
        # Number of position allocated in array
        num_field_expec = ''
        
        # Store the index of identifier
        id_idx = i

        # Fetch information from symbol table
        value, type, _ = table.get_by_id(tokens[i + 2].val)

        # Expect the number be integer
        if type == "int":
            num_field_expec = value

            # Check if array statement has closing ] (right_bracket)
            check_if(
                tokens[i + 3].type,
                "right_bracket",
                "Expected ] after expression in array statement",
                tokens[i + 3].line_num,
            )
            # Position indice to end of array declaration (right bracket)
            i += 3
        elif tokens[i + 2].type == "right_bracket":
            # Define max array length
            num_field_expec =  ''
            # Position indice to end of array declaration (right bracket)
            i += 2
        else:
            error("Expected integer number after expression in array statement", tokens[i + 2].line_num)  

        # Check if array is also initialized
        if i + 1 < len(tokens) and tokens[i + 1].type == "assignment":
            
            # Check if expression follows = in array statement
            op_value, op_type, i = array_initializer(
                tokens,
                i + 2,
                table,
                num_field_expec,
                "Required expression after assignment operator",
            )

            # Modify datatype of the identifier
            table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]

            # Return the opcode and i (the token after var statement)
            return (
                OpCode(
                    "array_assign",
                    table.symbol_table[tokens[id_idx].val][0] + "---" + str(num_field_expec) + "---" + op_value,
                    prec_to_type[op_type],
                ),
                i,
                op_type,
            )
        elif i + 1 < len(tokens) and tokens[i + 1].type in invalid_tokens:
            error("Invalid Syntax for declaration", tokens[i].line_num)
        else:
            # Get the value from symbol table by id
            value, type, _ = table.get_by_id(tokens[id_idx].val)

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
            table.symbol_table[tokens[id_idx].val][1] = "declared"

            return (OpCode("array_no_assign", value + "---" + str(num_field_expec)), i, func_ret_type)
            
    # Check if variable is also initialized
    elif i + 1 < len(tokens) and tokens[i + 1].type == "assignment":
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
    from .simc_parser import expression

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
        "bitwise_and_equal" : "&=",
        "bitwise_xor_equal":"^=",
        "bitwise_or_equal":"|=",
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
            "bitwise_and_equal",
            "bitwise_xor_equal",
            "bitwise_or_equal",
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