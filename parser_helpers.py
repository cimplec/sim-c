from global_helpers import error


def check_if(given_type, should_be_types, msg, line_num):
    """
    Check if type matches what it should be otherwise throw an error and exit

    Params
    ======
    given_type      (string)      = Type of token to be checked
    should_be_types (string/list) = Type(s) to be compared with
    msg             (string)      = Error message to print in case some case fails
    line_num        (int)         = Line number
    """

    # Convert to list if type is string
    if type(should_be_types) == str:
        should_be_types = [should_be_types]

    # If the given_type is not part of should_be_types then throw error and exit
    if given_type not in should_be_types:
        error(msg, line_num)


def expression(
    tokens,
    i,
    table,
    msg,
    accept_unkown=False,
    accept_empty_expression=False,
    expect_paren=True,
    func_ret_type={},
):
    """
    Parse and expression from tokens

    Params
    ======
    tokens                  (list)        = List of tokens
    i                       (string/list) = Current index in list of tokens
    table                   (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    msg                     (string)      = Error message to print in case some case fails
    accept_unkown           (bool)        = Accept unknown type for variable or not
    accept_empty_expression (bool)        = Accept empty expression or not
    expect_paren            (bool)        = Expect parenthesis at the end
    func_ret_type           (string)      = Functions return type

    Returns
    =======
    string, string, int: The expression, datatype of the expression and the current index in source
                         code after parsing
    """

    # Initial values
    op_value = ""
    op_type = -1

    # Mapping for precedence checking (double > float > int)
    type_to_prec = {"int": 3, "float": 4, "double": 5}

    # Loop until expression is not parsed completely
    while i < len(tokens) and tokens[i].type in [
        "number",
        "input",
        "string",
        "id",
        "plus",
        "minus",
        "multiply",
        "divide",
        "comma",
        "equal",
        "not_equal",
        "greater_than",
        "less_than",
        "greater_than_equal",
        "less_than_equal",
        "modulus",
        "increment",
        "decrement",
        "plus_equal",
        "minus_equal",
        "multiply_equal",
        "divide_equal",
        "modulus_equal",
        "and",
        "or",
        "left_paren",
        "exit",
        "right_paren",
        "newline",
        "call_end",
        "address_of",
        "right_shift",
        "left_shift",
    ]:
        # Check for function call
        if tokens[i].type == "id" and tokens[i + 1].type == "left_paren":
            fun_opcode, i, func_ret_type = function_call_statement(
                tokens, i, table, func_ret_type
            )
            val = fun_opcode.val.split("---")
            params = val[1].split("&&&")
            op_value += val[0] + "(" + ", ".join(params)
            type_to_prec = {"string": 1, "char": 2, "int": 3, "float": 4, "double": 5}
            op_type = type_to_prec[table.get_by_id(table.get_by_symbol(val[0]))[1]]
            i -= 1
        # If token is identifier or constant
        elif tokens[i].type in ["number", "string", "id"]:
            # Fetch information from symbol table
            value, type, typedata = table.get_by_id(tokens[i].val)

            if type == "string":
                # If { in string then it is a f-string
                if "{" in value:
                    vars = []
                    temp_var = ""
                    enter = False

                    # Collect the variable names
                    for char in value:
                        if char == "{":
                            enter = True
                        elif char == "}":
                            vars.append(temp_var[1:])
                            temp_var = ""
                            enter = False

                        if enter:
                            temp_var += char

                    # Determine the type of variables and append the name of variables at the end
                    type_to_fs = {
                        "char": "%c",
                        "string": "%s",
                        "int": "%d",
                        "float": "%f",
                        "double": "%lf",
                    }
                    for var in vars:
                        _, type, _ = table.get_by_id(table.get_by_symbol(var))
                        if type == "var":
                            error("Unknown variable %s" % var, tokens[i].line_num)
                        value = value.replace(var, type_to_fs[type])
                        value += ", " + var

                    # Replace all {} in string
                    value = value.replace("{", "").replace("}", "")

                op_value += value
                op_type = 0 if typedata == "constant" else 1
            elif type == "char":
                op_value += value
                op_type = 2
            elif type == "int":
                op_value += str(value)
                op_type = (
                    type_to_prec["int"] if type_to_prec["int"] > op_type else op_type
                )
            elif type == "float":
                op_value += str(value)
                op_type = (
                    type_to_prec["float"]
                    if type_to_prec["float"] > op_type
                    else op_type
                )
            elif type == "double":
                op_value += str(value)
                op_type = (
                    type_to_prec["double"]
                    if type_to_prec["double"] > op_type
                    else op_type
                )
            elif type in ["var", "declared"] and not accept_unkown:
                error("Cannot find the type of %s" % value, tokens[i].line_num)
            elif type == "var" and accept_unkown:
                op_value += str(value)
        elif tokens[i].type in ["newline", "call_end"]:
            break
        else:
            word_to_op = {
                "plus": " + ",
                "minus": " - ",
                "multiply": " * ",
                "divide": " / ",
                " comma ": ", ",
                "equal": " == ",
                "not_equal": " != ",
                "greater_than": " > ",
                "less_than": " < ",
                "greater_than_equal": " >= ",
                "less_than_equal": " <= ",
                "input": " scanf ",
                "modulus": " % ",
                "increment": " ++ ",
                "decrement": " -- ",
                "plus_equal": " += ",
                "minus_equal": " -= ",
                "multiply_equal": " *= ",
                "divide_equal": " /= ",
                "modulus_equal": " %= ",
                "and": " && ",
                "or": " || ",
                "comma": ",",
                "left_paren": "(",
                "right_paren": ")",
                "address_of": "&",
                "left_shift": " << ",
                "right_shift": " >> ",
            }

            if (
                expect_paren
                and tokens[i].type == "right_paren"
                and tokens[i + 1].type in ["newline", "left_brace"]
            ):
                break

            op_value += word_to_op[tokens[i].type]

        i += 1

    # If expression is empty then throw an error
    if op_value == "" and not accept_empty_expression:
        error(msg, tokens[i].line_num)

    # Check if statement is of type input
    if " scanf " in op_value:

        # Check if there exists a prompt message
        if '"' in op_value:
            i1 = op_value.index('"') + 1
            i2 = op_value.index('"', i1)
            # Extracting the prompt
            p_msg = op_value[i1:i2]
            # Checking if dtype is mentioned
            if "'" in op_value[i2 + 1 :]:
                i1 = op_value.index("'", i2 + 1) + 1
                i2 = op_value.index("'", i1)
                dtype = op_value[i1:i2]
            else:
                # default dtype is string
                dtype = "s"
        else:
            p_msg = ""
            dtype = "s"
        dtype_to_prec = {"i": 3, "f": 4, "d": 5, "s": 1}
        op_value = str(p_msg) + "---" + str(dtype)
        op_type = dtype_to_prec[dtype]

    # Return the expression, type of expression, and current index in source codes
    return op_value, op_type, i, func_ret_type


def check_ptr(tokens, i):
    # Check if a pointer is being declared
    is_ptr = False
    # Count the depth of pointer
    count_ast = 0
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
