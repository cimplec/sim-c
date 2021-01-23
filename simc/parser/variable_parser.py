from ..global_helpers import error, check_if

from ..op_code import OpCode


def check_ptr(tokens, i):
    # Check if a pointer is being declared
    is_ptr = False

    # Count the depth of pointer
    count_ast = 0

    if tokens[i].type == "multiply":
        asterisk_count = 0

        # Accumulate count of * in j
        while tokens[i + asterisk_count].type == "multiply":
            asterisk_count += 1

        # Add asterisk count to token index to get index of token after all asterisks
        i += asterisk_count

        is_ptr = True
        return is_ptr, asterisk_count, i
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

    # Check if the variable is a pointer, and if it is then get the depth of pointer
    is_ptr, asterisk_count, i = check_ptr(tokens, i)

    # Check if identifier is present after var
    check_if(got_type=tokens[i].type, should_be_types="id",
             error_msg="Expected id after var keyword", line_num=tokens[i].line_num)

    # Tokens that are not accepted after declaration of a variable
    invalid_tokens = [
        # Shortcut arithmetic assignments
        "plus_equal",
        "minus_equal",
        "multiply_equal",
        "divide_equal",
        "modulus_equal",

        # Arithmetic operators
        "plus",
        "minus",
        "multiply",
        "divide",
        "modulus",

        # Bitwise operators
        "bitwise_and",
        "bitwise_or",
        "bitwise_xor",

        # Shortcut bitwise assignments
        "bitwise_and_equal",
        "bitwise_or_equal",
        "bitwise_xor_equal",

        # Relational operators
        "equal",
        "not_equal",
    ]

    # Map datatype to appropriate datatype in C
    prec_to_type = {
        -1: "declared",
        0: "string",
        1: "char*",
        2: "char",
        3: "int",
        4: "float",
        5: "double",
        6: "bool",
    }

   # Check if it is an array declaration (+ initializer list)
    if tokens[i + 1].type == "left_bracket":

        # Size of array
        size_of_array = ""

        # Store the index of identifier
        id_idx = i

        # If the next token after [ is a number
        if tokens[i + 2].type == "number":
            # Fetch information from symbol table
            value, type_, _, _ = table.get_by_id(tokens[i + 2].val)

            if type_ == "int":
                size_of_array = value
            else:
                error(f"Expected integer size of array but got {type_}", tokens[i+2].line_num)

            # Check if array statement has closing ] (right_bracket)
            check_if(
                got_type=tokens[i + 3].type,
                should_be_types="right_bracket",
                error_msg="Expected ] after expression in array statement",
                line_num=tokens[i + 3].line_num,
            )

            # Move token index to end of array declaration (right bracket)
            i += 3
        elif tokens[i + 2].type == "right_bracket":
            # Size of array is not known
            size_of_array = ""

            # Move token index to end of array declaration (right bracket)
            i += 2

        # Check if array is initialized as var <name>[] = {1, 2, ...} 
        if i + 1 < len(tokens) and tokens[i + 1].type == "assignment":
            # Check if expression follows = in array statement
            op_value, op_type, i = array_initializer(
                tokens,
                i + 2,
                table,
                size_of_array,
                "Required expression after assignment operator",
            )
            i += 1

            # Modify datatype of the identifier
            table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]

            # Add the size of array to metadata (typedata) in symbol table
            table.symbol_table[tokens[id_idx].val][2] = size_of_array if size_of_array != "" else -1

            # Return the opcode and i (the token after var statement)
            return (
                OpCode(
                    "array_assign",
                    table.symbol_table[tokens[id_idx].val][0]
                    + "---"
                    + str(size_of_array)
                    + "---"
                    + op_value,
                    prec_to_type[op_type],
                ),
                i,
                op_type,
            )
        elif i + 1 < len(tokens) and tokens[i + 1].type in invalid_tokens:
            error("Invalid Syntax for declaration", tokens[i].line_num)
        else:
            # Get the value from symbol table by id
            value, type_, _, _ = table.get_by_id(tokens[id_idx].val)

            # If already declared then throw error
            if type_ in [
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

            # Set type to declared
            table.symbol_table[tokens[id_idx].val][1] = "arr_declared"

            # Check if size of array has been determined or not, it isn't then throw error
            # Since for later assignment size needs to be known
            if size_of_array == "":
                error("Size of array needs to be known if assignment is not done while declaration", tokens[i].line_num)
            else:
                table.symbol_table[tokens[id_idx].val][2] = size_of_array
            return (
                OpCode("array_no_assign", value + "---" + str(size_of_array)),
                i,
                func_ret_type,
            )


    # Check if variable is assigned with declaration
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
                    + str(asterisk_count),
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

    # If it is of pointer or variable type but has no value yet
    else:
        # Get the value from symbol table by id
        value, type, _, _ = table.get_by_id(tokens[i].val)

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
            "bool",
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
    from .array_parser import array_initializer
    
    # Map datatype to appropriate datatype in C
    prec_to_type = {
        -1: "declared",
        0: "string",
        1: "char*",
        2: "char",
        3: "int",
        4: "float",
        5: "double",
        6: "bool",
    }
    
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
    var_name, type_, _, _ = table.get_by_id(tokens[i - 1].val)

    if type_ == "var":
        error("Variable %s used before declaration" % var_name, tokens[i - 1].line_num)

    # Index of assignment in array
    op_value_idx = ""

    # Store the index of identifier
    id_idx = i - 1

    # Store the id of variable in Symbol Table
    var_id = tokens[id_idx].val
    
    # Check if is a array indexing case
    if tokens[i].type == "left_bracket":
        if(tokens[i + 1].type == "number"):
            # Fetch information from symbol table
            value, type_, _, _ = table.get_by_id(tokens[i + 1].val)

            if type_ == "int":
                if int(value) >= int(table.symbol_table[tokens[id_idx].val][2]):
                    error(f"Index {value} out of bounds for array {var_name}", tokens[i].line_num )
            else:
                error("Expected integer value or expression in array idexing", tokens[i].line_num) 
        
        op_value_idx, op_type_idx, i, func_ret_type = expression(
            tokens,
            i,
            table,
            "Expected integer an index for array",
            block_type_promotion=True,
            expect_paren=False,
            func_ret_type=func_ret_type,
        ) 

        # Type 3 is for integer expressions
        if op_type_idx != 3:
            error("Expected integer value or expression in array idexing", tokens[i].line_num)    
        

    # Dictionary to convert tokens to their corresponding assignment types
    assignment_type = {
        "assignment": "=",
        "plus_equal": "+=",
        "minus_equal": "-=",
        "multiply_equal": "*=",
        "divide_equal": "/=",
        "modulus_equal": "%=",
        "bitwise_and_equal": "&=",
        "bitwise_xor_equal": "^=",
        "bitwise_or_equal": "|=",
    }

    check_if(
        got_type=tokens[i].type,
        should_be_types=[
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
        error_msg="Expected assignment operator after identifier",
        line_num=tokens[i].line_num,
    )
    
    # Convert the token to respective symbol
    converted_type = assignment_type[tokens[i].type]


    # Get the symbol table entry for the identifier
    id_table_entry = table.symbol_table[tokens[id_idx].val]
    type_ = id_table_entry[1]

    # Flag to check array assignment
    is_arr = False

    # Check if assignment is an array initializer or a simple expression type
    if tokens[i + 1].type == "left_brace":
        is_arr = True
        if type_ != "arr_declared":
            error("Cannot assign an initializer list to a variable", tokens[i].line_num)

        size_of_array = id_table_entry[2]

        op_value, op_type, i = array_initializer(
            tokens,
            i + 1,
            table,
            size_of_array,
            "Required expression after assignment operator",
        )

        # Modify datatype of the identifier
        table.symbol_table[var_id][1] = prec_to_type[op_type]

    else:
        if type_ == "arr_declared" and tokens[id_idx + 1].type != "left_bracket":
            error("Array assignment requires initializer list, cannot assign expression", tokens[i].line_num)

        # Check if expression follows = in assign statement
        op_value, op_type, i, func_ret_type = expression(
            tokens,
            i + 1,
            table,
            "Required expression after assignment operator",
            expect_paren=False,
            func_ret_type=func_ret_type,
        )
    
    op_value = converted_type + "---" + op_value

    if table.symbol_table[var_id][1] in ["var", "declared"]:
        # Modify datatype of the identifier
        table.symbol_table[var_id][1] = prec_to_type[op_type]
        
    # Check if a pointer is being assigned
    if is_ptr:
        return (
            OpCode(
                "ptr_only_assign",
                table.symbol_table[var_id][0] + op_value_idx
                + "---"
                + op_value
                + "---"
                + str(count_ast),
                "",
            ),
            i,
            func_ret_type,
        )

    # Resolve pendenting infer types
    table.resolve_dependency(tokens, i, var_id)

    # If it is an array then generate array_only_assign
    if is_arr:
        # Add (<type> [<size>]) to op_value
        op_value = " " + op_value.split("---")[0] + " (" + prec_to_type[op_type] + " [" + size_of_array + "])" + op_value.split("---")[1]
        return (
            OpCode(
                "array_only_assign", 
                table.symbol_table[var_id][0] + "---" + op_value, ""
            ),
            i,
            func_ret_type,
        )

    # Return the opcode and i (the token after assign statement)
    return (
        OpCode(
            "assign", var_name + op_value_idx + "---" + op_value, ""
        ),
        i,
        func_ret_type,
    )

