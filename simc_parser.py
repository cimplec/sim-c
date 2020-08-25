# Module to import some helper functions
from global_helpers import error

# Module to import parser helper functions
from parser_helpers import check_if, expression, check_ptr

# Module to import OpCode class
from op_code import OpCode

# Module to import function for parsing looping statements
from loops import for_statement, while_statement

# Module to import function for parsing functions
from function import function_definition_statement, function_call_statement

# Module to import conditional statements
from conditionals import if_statement, switch_statement, case_statement

# Module to import print statement
from print import print_statement

# Module to import variables
from variables import var_statement, assign_statement


def unary_statement(tokens, i, table, func_ret_type):
    """
    Parse unary statement

    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

    Returns
    =======
    OpCode, int: The opcode for the unary code and the index after parsing unary statement

    Grammar
    =======
    unary_statement -> id operator
    id              -> [a-zA-Z_]?[a-zA-Z0-9_]*
    operator        -> ++ | --
    """

    # Check if assignment operator follows identifier name
    if tokens[i].type not in ["increment", "decrement"]:
        check_if(
            tokens[i + 1].type,
            ["increment", "decrement"],
            "Expected unary operator after identifier",
            tokens[i + 1].line_num,
        )
        # Check if expression follows = in assign statement
        op_value, _, i, func_ret_type = expression(
            tokens,
            i,
            table,
            "",
            accept_empty_expression=True,
            expect_paren=False,
            func_ret_type=func_ret_type,
        )
        # Return the opcode and i (the token after unary statement)
        return OpCode("unary", op_value), i, func_ret_type

    else:
        check_if(
            tokens[i + 1].type,
            "id",
            "Expected identifier after unary operator",
            tokens[i + 1].line_num,
        )
        op_value = -1
        if tokens[i].type == "increment":
            op_value = "++ --- "
        else:
            op_value = "-- --- "
        value, func_ret_type, _ = table.get_by_id(tokens[i + 1].val)
        op_value += str(value)
        return OpCode("unary", op_value), i + 2, func_ret_type


def exit_statement(tokens, i, table, func_ret_type):
    """
    Parse exit statement

    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

    Returns
    =======
    OpCode, int: The opcode for the assign code and the index after parsing exit statement

    Grammar
    =======
    exit_statement -> exit(expr)
    expr            -> number
    number          -> [0-9]+

    """
    # Check if ( follows exit statement
    check_if(
        tokens[i].type,
        "left_paren",
        "Expected ( after exit statement",
        tokens[i].line_num,
    )

    # Check if number follows ( in exit statement
    check_if(
        tokens[i + 1].type,
        "number",
        "Expected number after ( in exit statement",
        tokens[i].line_num,
    )

    # check if expression follows ( in exit statement
    op_value, _, i, func_ret_type = expression(
        tokens,
        i + 1,
        table,
        "Expected expression inside exit statement",
        func_ret_type=func_ret_type,
    )
    op_value_list = op_value.replace(" ", "").split(",")
    # check if ) follows expression in exit statement
    check_if(
        tokens[i - 1].type,
        "right_paren",
        "Expected ) after expression in exit statement",
        tokens[i - 1].line_num,
    )

    return OpCode("exit", op_value[:-1]), i, func_ret_type


def parse(tokens, table):
    """
    Parse tokens and generate opcodes

    Params
    ======
    tokens (list) = List of tokens

    Returns
    =======
    list: The list of opcodes

    Grammar
    =======
    statement -> print_statement | var_statement | assign_statement | function_definition_statement
    """

    # List of opcodes
    op_codes = []

    # Current function's name
    func_name = ""

    # Do while started or not
    in_do = False

    # Count main functions
    main_fn_count = 0

    # Count if conditions
    if_count = 0

    # If function return type could not be figured out during return then do it while calling
    func_ret_type = {}

    # Loop through all the tokens
    i = 0
    while i <= len(tokens) - 1:
        # If token is of type print then generate print opcode
        if tokens[i].type == "print":
            print_opcode, i, func_ret_type = print_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(print_opcode)
        # If token is of type var then generate var opcode
        elif tokens[i].type == "var":
            var_opcode, i, func_ret_type = var_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(var_opcode)
        # If token is of type id then generate assign opcode
        elif tokens[i].type == "id":
            # If '(' follows id then it is function calling else variable assignment
            if tokens[i + 1].type == "left_paren":
                fun_opcode, i, func_ret_type = function_call_statement(
                    tokens, i, table, func_ret_type
                )
                op_codes.append(fun_opcode)
            elif tokens[i + 1].type in ["increment", "decrement"]:
                unary_opcode, i, func_ret_type = unary_statement(
                    tokens, i, table, func_ret_type
                )
                op_codes.append(unary_opcode)
            else:
                assign_opcode, i, func_ret_type = assign_statement(
                    tokens, i + 1, table, func_ret_type
                )
                op_codes.append(assign_opcode)
        # If token is of type fun then generate function opcode
        elif tokens[i].type == "fun":
            fun_opcode, i, func_name, func_ret_type = function_definition_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(fun_opcode)
        # If token is of type left_brace then generate scope_begin opcode
        elif tokens[i].type == "left_brace":
            op_codes.append(OpCode("scope_begin", "", ""))
            i += 1
        # If token is of type right_brace then generate scope_over opcode
        elif tokens[i].type == "right_brace":
            op_codes.append(OpCode("scope_over", "", ""))
            i += 1
        # If token is of type MAIN then generate MAIN opcode
        elif tokens[i].type == "MAIN":
            op_codes.append(OpCode("MAIN", "", ""))
            main_fn_count += 1
            if main_fn_count > 1:
                error("Presence of two MAIN in a single file", tokens[i].line_num)
            i += 1
        # If token is of type END_MAIN then generate MAIN opcode
        elif tokens[i].type == "END_MAIN":
            op_codes.append(OpCode("END_MAIN", "", ""))
            main_fn_count -= 1
            i += 1
        # If token is of type for then generate for code
        elif tokens[i].type == "for":
            for_opcode, i, func_ret_type = for_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(for_opcode)
        # If token is of type do then generate do_while code
        elif tokens[i].type == "do":
            check_if(
                tokens[i + 1].type,
                "left_brace",
                "Expected { after do statement",
                tokens[i + 1].line_num,
            )
            in_do = True
            op_codes.append(OpCode("do", "", ""))
            i += 1
        # If token is of type while then generate while opcode
        elif tokens[i].type == "while":
            while_opcode, i, func_ret_type = while_statement(
                tokens, i + 1, table, in_do, func_ret_type
            )
            if in_do:
                in_do = False
            op_codes.append(while_opcode)
        # If token is of type if then generate if opcode
        elif tokens[i].type == "if":
            if_opcode, i, func_ret_type = if_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(if_opcode)

            # Increment if count on encountering if
            if_count += 1
        # If token is of type exit then generate exit opcode
        elif tokens[i].type == "exit":
            exit_opcode, i, func_ret_type = exit_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(exit_opcode)
        # If token is of type else then check whether it is else if or else
        elif tokens[i].type == "else":
            # If the next token is if, then it is else if
            if tokens[i + 1].type == "if":
                if_opcode, i, func_ret_type = if_statement(
                    tokens, i + 2, table, func_ret_type
                )
                if_opcode.type = "else_if"
                op_codes.append(if_opcode)
            # Otherwise it is else
            elif tokens[i + 1].type == "left_brace":
                op_codes.append(OpCode("else", "", ""))

                # Decrement if count on encountering if, to make sure there aren't extra else conditions
                if_count -= 1

                # If if_count is negative then the current else is extra
                if if_count < 0:
                    error("Else does not match any if!", tokens[i].line_num)

                i += 1
        # If token is of type return then generate return opcode
        elif tokens[i].type == "return":
            beg_idx = i + 1
            if tokens[i + 1].type not in ["id", "number"]:
                op_value = ""
                op_type = 6
                i += 2
            else:
                op_value, op_type, i, func_ret_type = expression(
                    tokens,
                    i + 1,
                    table,
                    "Expected expression after return",
                    True,
                    True,
                    expect_paren=False,
                    func_ret_type=func_ret_type,
                )
            if func_name == "":
                error("Return statement outside any function", tokens[i].line_num)
            else:
                #  Map datatype to appropriate datatype in C
                prec_to_type = {
                    -1: "not_known",
                    0: "char*",
                    1: "char*",
                    2: "char",
                    3: "int",
                    4: "float",
                    5: "double",
                    6: "void",
                }

                if op_type == -1:
                    func_ret_type[func_name] = beg_idx

                # Change return type of function
                table.symbol_table[table.get_by_symbol(func_name)][1] = prec_to_type[
                    op_type
                ]

                # Set func_name to an empty string after processing
                func_name = ""
            op_codes.append(OpCode("return", op_value, ""))
        # If token is of type break then generate break opcode
        elif tokens[i].type == "break":
            op_codes.append(OpCode("break", "", ""))
            i += 1
        # If token is of type continue then generate continue opcode
        elif tokens[i].type == "continue":
            op_codes.append(OpCode("continue", "", ""))
            i += 1
        # If token is of type single_line_statement then generate single_line_comment opcode
        elif tokens[i].type == "single_line_comment":
            op_codes.append(OpCode("single_line_comment", tokens[i].val, ""))
            i += 1
        # If token is of type multi_line_statement then generate multi_line_comment opcode
        elif tokens[i].type == "multi_line_comment":
            op_codes.append(OpCode("multi_line_comment", tokens[i].val, ""))
            i += 1
        # If token is of type switch then generate switch opcode
        elif tokens[i].type == "switch":
            switch_opcode, i, func_ret_type = switch_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(switch_opcode)
        # If token is of type case then generate case opcode
        elif tokens[i].type == "case":
            case_opcode, i, func_ret_type = case_statement(
                tokens, i + 1, table, func_ret_type
            )
            op_codes.append(case_opcode)
        # If token is of type default then generate default opcode
        elif tokens[i].type == "default":
            check_if(
                tokens[i + 1].type,
                "colon",
                "Expected : after default statement in switch",
                tokens[i + 1].line_num,
            )
            op_codes.append(OpCode("default", "", ""))
            i += 2
        # If token is the type increment or decrement then generate unary_opcode
        elif tokens[i].type in ["increment", "decrement"]:
            unary_opcode, i, func_ret_type = unary_statement(
                tokens, i, table, func_ret_type
            )
            op_codes.append(unary_opcode)

        # Otherwise increment the index
        else:
            i += 1

    # Errors that may occur after parsing loop
    if main_fn_count != 0:
        error("MAIN not ended with END_MAIN", tokens[i - 1].line_num + 1)

    # Return opcodes
    return op_codes
