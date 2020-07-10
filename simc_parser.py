# Module to import some helper functions
from global_helpers import error

# Module to import OpCode class
from op_code import OpCode

def check_if(given_type, should_be_types, msg):
    """
        Check if type matches what it should be otherwise throw an error and exit

        Params
        ======
        given_type      (string)      = Type of token to be checked
        should_be_types (string/list) = Type(s) to be compared with
        msg             (string)      = Error message to print in case some case fails
    """

    # Convert to list if type is string
    if(type(should_be_types) == str):
        should_be_types = [should_be_types]

    # If the given_type is not part of should_be_types then throw error and exit
    if(given_type not in should_be_types):
        error(msg)

def expression(tokens, i, table, msg, accept_unkown=False, accept_empty_expression=False):
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

        Returns
        =======
        string, string, int: The expression, datatype of the expression and the current index in source
                             code after parsing
    """

    # Initial values
    op_value = ""
    op_type = -1

    # Mapping for precedence checking (double > float > int)
    type_to_prec = {'int': 3, 'float': 4, 'double': 5}

    # Loop until expression is not parsed completely
    while(i < len(tokens) and tokens[i].type in ['number', 'input', 'string', 'id', 'plus', 'minus', 'multiply', 'divide', 'comma', 'equal', 'not_equal', 'greater_than', 'less_than', 'greater_than_equal', 'less_than_equal', 'modulus', 'increment', 'decrement', 'plus_equal', 'minus_equal', 'multiply_equal', 'divide_equal', 'modulus_equal', 'and', 'or']):
        # If token is identifier or constant
        if(tokens[i].type in ['number', 'string', 'id']):
            # Fetch information from symbol table
            value, type, typedata = table.get_by_id(tokens[i].val)

            if(type == 'string'):
                # If { in string then it is a f-string
                if("{" in value):
                    vars = []
                    temp_var = ""
                    enter = False

                    # Collect the variable names
                    for char in value:
                        if(char == "{"):
                            enter = True
                        elif(char == "}"):
                            vars.append(temp_var[1:])
                            temp_var = ""
                            enter = False

                        if(enter):
                            temp_var += char

                    # Determine the type of variables and append the name of variables at the end
                    type_to_fs = {"char": "%c", "string": "%s", "int": "%d", "float": "%f", "double": "%lf"}
                    for var in vars:
                        _, type, _ = table.get_by_id(table.get_by_symbol(var))
                        if(type == "var"):
                            error("Unknown variable %s" % var)
                        value = value.replace(var, type_to_fs[type])
                        value += ", " + var

                    # Replace all {} in string
                    value = value.replace("{", "").replace("}", "")
                    
                op_value += value
                op_type = 0 if typedata == 'constant' else 1
            elif(type == 'char'):
                op_value += value
                op_type = 2
            elif(type == 'int'):
                op_value += str(value)
                op_type = type_to_prec['int'] if type_to_prec['int'] > op_type else op_type
            elif(type == 'float'):
                op_value += str(value)
                op_type = type_to_prec['float'] if type_to_prec['float'] > op_type else op_type
            elif(type == 'double'):
                op_value += str(value)
                op_type = type_to_prec['double'] if type_to_prec['double'] > op_type else op_type
            elif(type == 'var' and not accept_unkown):
                error("Cannot find the type of %s" % value)
            elif(type == 'var' and accept_unkown):
                op_value += str(value)
        elif(tokens[i].type == 'newline'):
            break
        else:
            if(tokens[i].type == 'plus'):
                op_value += ' + '
            elif(tokens[i].type == 'minus'):
                op_value += ' - '
            elif(tokens[i].type == 'multiply'):
                op_value += ' * '
            elif(tokens[i].type == 'divide'):
                op_value += ' / '
            elif(tokens[i].type == 'comma'):
                op_value += ', '
            elif(tokens[i].type == 'equal'):
                op_value += ' == '
            elif(tokens[i].type == 'not_equal'):
                op_value += ' != '
            elif(tokens[i].type == 'greater_than'):
                op_value += ' > '
            elif(tokens[i].type == 'less_than'):
                op_value += ' < '
            elif(tokens[i].type == 'greater_than_equal'):
                op_value += ' >= '
            elif(tokens[i].type == 'less_than_equal'):
                op_value += ' <= '
            elif(tokens[i].type == 'input'):
                op_value += ' scanf '
            elif(tokens[i].type == 'modulus'):
                op_value += ' % '
            elif(tokens[i].type == 'increment'):
                op_value += ' ++ '
            elif(tokens[i].type == 'decrement'):
                op_value += ' -- '
            elif(tokens[i].type == 'plus_equal'):
                op_value += ' += '
            elif(tokens[i].type == 'minus_equal'):
                op_value += ' -= '
            elif(tokens[i].type == 'multiply_equal'):
                op_value += ' *= '
            elif(tokens[i].type == 'divide_equal'):
                op_value += ' /= '
            elif(tokens[i].type == 'modulus_equal'):
                op_value += ' %= '
            elif(tokens[i].type == 'and'):
                op_value += ' && '
            elif(tokens[i].type == 'or'):
                op_value += ' || '

        i += 1


    # If expression is empty then throw an error
    if(op_value == "" and not accept_empty_expression):
        error(msg)

    #Check if statement is of type input
    if ' scanf ' in op_value:

        #Check if there exists a prompt message
        if('"' in op_value):
            i1 = op_value.index('"')+1
            i2 = op_value.index('"',i1)
            #Extracting the prompt
            p_msg = op_value[i1:i2]
            #Checking if dtype is mentioned
            if('\'' in op_value[i2+1:]):
                i1 = op_value.index('\'',i2+1)+1
                i2 = op_value.index('\'',i1)
                dtype = op_value[i1:i2]
            else:
                #default dtype is string
                dtype = 's'
        else:
            p_msg = ""
            dtype = 's'
        dtype_to_prec = {'i': 3, 'f': 4, 'd': 5, 's': 1}
        op_value = str(p_msg)+'---'+str(dtype)
        op_type = dtype_to_prec[dtype]


    # Return the expression, type of expression, and current index in source codes
    return op_value, op_type, i

def print_statement(tokens, i, table):
    """
        Parse print statement

        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

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
    check_if(tokens[i].type, "left_paren", "Expected ( after print statement")

    # Check if expression follows ( in print statement
    op_value, op_type, i = expression(tokens, i+1, table, "Expected expression inside print statement")

    # Map datatype to appropriate format specifiers
    prec_to_type = {0: "", 1: "\"%s\", ", 2: "\"%c\", ", 3: "\"%d\", ", 4: "\"%f\", ", 5: "\"%lf\", "}
    op_value = prec_to_type[op_type] + op_value

    # Check if print statement has closing )
    check_if(tokens[i].type, "right_paren", "Expected ) after expression in print statement")

    # Return the opcode and i+1 (the token after print statement)
    return OpCode("print", op_value), i+1

def var_statement(tokens, i, table):
    """
        Parse variable declaration [/initialization] statement

        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

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

    # Check if identifier is present after var
    check_if(tokens[i].type, "id", "Expected id after var keyword")

    # Check if variable is also initialized
    if(i+1 < len(tokens) and tokens[i+1].type == 'assignment'):
        # Store the index of identifier
        id_idx = i

        # Check if expression follows = in var statement
        op_value, op_type, i = expression(tokens, i+2, table, "Required expression after assignment operator")

        # Map datatype to appropriate datatype in C
        prec_to_type = {0: "string", 1: "string", 2: "char", 3: "int", 4: "float", 5: "double"}

        # Modify datatype of the identifier
        table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]

        # Return the opcode and i (the token after var statement)
        return OpCode("var_assign", table.symbol_table[tokens[id_idx].val][0] + '---' + op_value, prec_to_type[op_type]), i
    else:
        # Get the value from symbol table by id
        value, _, _ = table.get_by_id(tokens[i].val)

        # Return the opcode and i+1 (the token after var statement)
        return OpCode("var_no_assign", value), i+1

def assign_statement(tokens, i, table):
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

    # Check if assignment operator follows identifier name
    check_if(tokens[i].type, ["assignment", "plus_equal", "minus_equal", "multiply_equal", "divide_equal", "modulus_equal"], "Expected assignment operator after identifier")

    # Store the index of identifier
    id_idx = i-1

    # Check if expression follows = in assign statement
    op_value, op_type, i = expression(tokens, i, table, "Required expression after assignment operator")

    #  Map datatype to appropriate datatype in C
    prec_to_type = {0: "string", 1: "string", 2: "char", 3: "int", 4: "float", 5: "double"}

    # Modify datatype of the identifier
    table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]

    # Return the opcode and i (the token after assign statement)
    return OpCode("assign", table.symbol_table[tokens[id_idx].val][0] + '---' + op_value, ""), i

def function_definition_statement(tokens, i, table):
    """
        Parse function definition statement

        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

        Returns
        =======
        OpCode, int, string: The opcode for the assign code, the index, and the name of the functionafter
                             parsing function calling statement

        Grammar
        =======
        function_definition_statement   -> fun id([formal_params,]*) { body }
        formal_params                   -> expr
        body                            -> statement
        expr                            -> string | number | id | operator
        string                          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
        quote                           -> "
        number                          -> [0-9]+
        id                              -> [a-zA-Z_]?[a-zA-Z0-9_]*
        operator                        -> + | - | * | /
    """

    # Check if identifier follows fun
    check_if(tokens[i].type, "id", "Expected function name")

    # Store the id of function name in symbol table
    func_idx = tokens[i].val

    # Get function name
    func_name, _, _ = table.get_by_id(func_idx)

    # Check if ( follows id in function
    check_if(tokens[i+1].type, "left_paren", "Expected ( after function name")

    # Check if expression follows ( in function statement
    op_value, op_type, i = expression(tokens, i+2, table, "", True, True)
    op_value_list = op_value.replace(" ", "").split(",")

    # Check if ) follows expression in function
    check_if(tokens[i].type, "right_paren", "Expected ) after function params list")

    # Check if { follows ) in function
    check_if(tokens[i+1].type, "left_brace", "Expected { before function body")

    # Loop until } is reached
    i += 2
    ret_idx = i
    found_right_brace = False
    while(i < len(tokens) and tokens[i].type != "right_brace"):
        if(tokens[i].type == "right_brace"):
            found_right_brace = True
        i += 1

    # If right brace found at end
    if(i != len(tokens) and tokens[i].type == "right_brace"):
        found_right_brace = True

    # If right brace is not found then produce error
    if(not found_right_brace):
        error("Expected } after function body")

    # Add the identifier types to function's typedata
    table.symbol_table[func_idx][2] = "function---" + "---".join(op_value_list) if len(op_value_list) > 0 and len(op_value_list[0]) > 0 else "function"

    return OpCode("func_decl", func_name + '---' + "&&&".join(op_value_list), ""), ret_idx, func_name

def function_call_statement(tokens, i, table):
    """
        Parse function calling statement

        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

        Returns
        =======
        OpCode, int: The opcode for the assign code and the index after parsing function calling statement

        Grammar
        =======
        function_call_statement   -> id([actual_params,]*)
        actual_params             -> expr
        body                      -> statement
        expr                      -> string | number | id | operator
        string                    -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
        quote                     -> "
        number                    -> [0-9]+
        id                        -> [a-zA-Z_]?[a-zA-Z0-9_]*
        operator                  -> + | - | * | /
    """

    # Get information about the function from symbol table
    func_name, _, metadata = table.get_by_id(tokens[i].val)

    # Extract params from functions metadata (typedata), these are stored as <id>---[<param 1>, . . . , <param n>]
    params = metadata.split('---')[1:] if '---' in metadata else []

    # Parse the params
    op_value, op_type, i = expression(tokens, i+2, table, "", True, True)
    op_value_list = op_value.replace(" ", "").split(",")
    op_value_list = op_value_list if len(op_value_list) > 0 and len(op_value_list[0]) > 0 else []

    # Check if number of actual and formal parameters match
    if(len(params) != len(op_value_list)):
        error("Expected %d parameters but got %d parameters in function %s" %
                (len(params), len(op_value_list), func_name))

    # Check if ) follows params in function calling
    check_if(tokens[i].type, "right_paren", "Expected ) after params in function calling")

    # Assign datatype to formal parameters
    for j in range(len(params)):
        # Fetch the datatype of corresponding actual parameter from symbol table
        _, dtype, _ = table.get_by_id(table.get_by_symbol(op_value_list[j]))

        # Set the datatype of the formal parameter
        table.symbol_table[table.get_by_symbol(params[j])][1] = dtype

    return OpCode("func_call", func_name + "---" + "&&&".join(op_value_list), ""), i+1

def while_statement(tokens, i, table):
    """
        Parse while statement

        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

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
    #Check if ( follows while statement
    check_if(tokens[i].type, "left_paren", "Expected ( after while statement")

    #check if expression follows ( in while statement
    op_value, _, i = expression(tokens, i+1, table, "Expected expression inside while statement")

    # check if ) follows expression in while statement
    check_if(tokens[i].type, "right_paren",
             "Expected ) after expression in while statement")

    #Check if { follows ) in while statement
    check_if(tokens[i+1].type, "left_brace", "Expected { before while loop body")

    # Loop until } is reached
    i += 2
    ret_idx = i
    found_right_brace = False
    while(i < len(tokens) and tokens[i].type != "right_brace"):
        if(found_right_brace):
            found_right_brace = True
        i += 1

    # If right brace found at end
    if(i != len(tokens) and tokens[i].type == "right_brace"):
        found_right_brace = True

    # If right brace is not found then produce error
    if(not found_right_brace):
        error("Expected } after while loop body")

    return OpCode("while", op_value), ret_idx


def if_statement(tokens, i, table):
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
    #Check if ( follows if statement
    check_if(tokens[i].type, "left_paren", "Expected ( after if statement")

    #check if expression follows ( in if statement
    op_value, op_type, i = expression(
        tokens, i+1, table, "Expected expression inside if statement")
    op_value_list = op_value.replace(" ", "").split(",")
    # check if ) follows expression in if statement
    check_if(tokens[i].type, "right_paren",
             "Expected ) after expression in if statement")

    #Check if { follows ) in if statement
    check_if(tokens[i+1].type, "left_brace",
             "Expected { before if body")

    # Loop until } is reached
    i += 2
    ret_idx = i
    found_right_brace = False
    while(i < len(tokens) and tokens[i].type != "right_brace"):
        if(found_right_brace):
            found_right_brace = True
        i += 1

    # If right brace found at end
    if(i != len(tokens) and tokens[i].type == "right_brace"):
        found_right_brace = True

    # If right brace is not found then produce error
    if(not found_right_brace):
        error("Expected } after if body")

    return OpCode("if", op_value), ret_idx

def for_loop(tokens, i, table):
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
    check_if(tokens[i].type, "id", "Expected variable name")

    # Check if in follows identifier
    check_if(tokens[i+1].type, "in", "Expected in keyword")

    # Check if number follows in keyword
    check_if(tokens[i+2].type, "number", "Expected starting value")

    # Check if to keyword follows number
    check_if(tokens[i+3].type, "to", "Expected to keyword")

    # Check if number follows in keyword
    check_if(tokens[i+4].type, "number", "Expected ending value")

    # Check if by keyword follows number
    check_if(tokens[i+5].type, "by", "Expected by keyword")

    word_to_op = {"plus": "+", "minus": "-", "multiply": "*", "divide": "/"}

    # Check if number follows operator
    check_if(tokens[i+7].type, "number", "Expected value for change")

    #Get required values
    var_name, _, _ = table.get_by_id(tokens[i].val)
    table.symbol_table[tokens[i].val][1] = "int"
    starting_val, _, _ = table.get_by_id(tokens[i+2].val)
    ending_val, _, _ = table.get_by_id(tokens[i+4].val)
    operator_type = word_to_op[tokens[i+6].type]
    change_val, _, _ = table.get_by_id(tokens[i+7].val)

    # To determine the > or < sign
    if starting_val > ending_val:
        sign_needed = ">"
    else:
        sign_needed = "<"

    # Return the opcode and i+1 (the token after for loop statement)
    return OpCode("for", str(var_name) + '&&&' + str(starting_val) + '&&&' + str(ending_val) + '&&&' + str(operator_type) + '&&&' + sign_needed + '&&&' + str(change_val)), i+1

def unary_statement(tokens, i, table):
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
    check_if(tokens[i+1].type, ["increment", "decrement"], "Expected unary operator after identifier")

    # Check if expression follows = in assign statement
    op_value, _, i = expression(
        tokens, i, table, "", accept_empty_expression=True)

    # Return the opcode and i (the token after unary statement)
    return OpCode("unary", op_value), i

def do_while_statement (tokens, i, table):
    """
        Parse do while statement

        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

        Returns
        =======
        OpCode, int: The opcode for the assign code and the index after parsing do while statement

        Grammar
        =======
        do_while_statement  -> do { body } while ( condition )
        condition           -> expr
        expr                -> string | number | id | operator
        string              -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
        quote               -> "
        number              -> [0-9]+
        id                  -> [a-zA-Z_]?[a-zA-Z0-9_]*
        operator            -> + | - | * | /
    """
    #Check if { follows do statement
    check_if(tokens[i].type, "left_brace", "Expected { after do statement")

    # Loop until } is reached
    i += 2
    ret_idx = i
    found_right_brace = False
    while(i < len(tokens) and tokens[i].type != "right_brace"):
        if(found_right_brace):
            found_right_brace = True
        i += 1

    # If right brace found at end
    if(i != len(tokens) and tokens[i].type == "right_brace"):
        found_right_brace = True

    # If right brace is not found then produce error
    if(not found_right_brace):
        error("Expected } after do statement body")
    
    #Check if while follows do statement
    check_if(tokens[i+1].type, "while", "Expected while statement after do body")

    #Check if ( follows while statement
    check_if(tokens[i+2].type, "left_paren", "Expected ( after while statement")
    
    #check if expression follows ( in while statement
    op_value, _, i = expression(
        tokens, i+3, table, "Expected expression inside while statement")

    # check if ) follows expression in while statement
    check_if(tokens[i].type, "right_paren",
             "Expected ) after expression in while statement")

    return OpCode("do_while", op_value), ret_idx

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

    # Loop through all the tokens
    i = 0

    #boolean determining while or do_while loop
    do = False

    while(i <= len(tokens) - 1):
        # If token is of type print then generate print opcode
        if tokens[i].type == "print":
            print_opcode, i = print_statement(tokens, i+1, table)
            op_codes.append(print_opcode)
        # If token is of type var then generate var opcode
        elif tokens[i].type == "var":
            var_opcode, i = var_statement(tokens, i+1, table)
            op_codes.append(var_opcode)
        # If token is of type id then generate assign opcode
        elif tokens[i].type == "id":
            # If ( follows id then it is function calling else variable assignment
            if(tokens[i+1].type == "left_paren"):
                fun_opcode, i = function_call_statement(tokens, i, table)
                op_codes.append(fun_opcode)
            elif(tokens[i+1].type in ["increment", "decrement"]):
                unary_opcode, i = unary_statement(tokens, i, table)
                op_codes.append(unary_opcode)
            else:
                assign_opcode, i = assign_statement(tokens, i+1, table)
                op_codes.append(assign_opcode)
        # If token is of type fun then generate function opcode
        elif tokens[i].type == "fun":
            fun_opcode, i, func_name = function_definition_statement(tokens, i+1, table)
            op_codes.append(fun_opcode)
        # If token is of type right_brace then generate scope_over opcode
        elif tokens[i].type == "right_brace":
            op_codes.append(OpCode("scope_over", "", ""))
            i += 1
        # If token is of type MAIN then generate MAIN opcode
        elif tokens[i].type == "MAIN":
            op_codes.append(OpCode("MAIN", "", ""))
            i += 1
        # If token is of type END_MAIN then generate MAIN opcode
        elif tokens[i].type == "END_MAIN":
            op_codes.append(OpCode("END_MAIN", "", ""))
            i += 1
        # If token is of type for then generate for code
        elif tokens[i].type == "for":
            for_opcode, i = for_loop(tokens, i+1, table)
            op_codes.append(for_opcode)
        # If token is of type while then generate while opcode
        elif tokens[i].type == "while":
            if (do == False):
                while_opcode, i = while_statement(tokens, i+1, table)
                op_codes.append(while_opcode)
            else:
                break
        # If token is of type if then generate if opcode
        elif tokens[i].type == "if":
            if_opcode, i = if_statement(tokens, i+1, table)
            op_codes.append(if_opcode)
        # If token is of type else then check whether it is else if or else
        elif tokens[i].type == "else":
            # If the next token is if, then it is else if
            if(tokens[i+1].type == "if"):
                if_opcode, i = if_statement(tokens, i+2, table)
                if_opcode.type = "else_if"
                op_codes.append(if_opcode)
            # Otherwise it is else
            elif(tokens[i+1].type == "left_brace"):
                print("World")
                op_codes.append(OpCode("else", "", ""))
                i += 2
            print(i, tokens[i])
        # If token is of type return then generate return opcode
        elif tokens[i].type == "return":
            op_value, op_type, i = expression(tokens, i+1, table, "Expected expression after return")
            if(func_name == ""):
                error("Return statement outside any function")
            else:
                #  Map datatype to appropriate datatype in C
                prec_to_type = {0: "char*", 1: "char*", 2: "char", 3: "int", 4: "float", 5: "double"}

                # Change return type of function
                table.symbol_table[table.get_by_symbol(func_name)][1] = prec_to_type[op_type]

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
        # If token is of type do then generate do_while opcode
        elif tokens[i].type == "do":
            do = True
            do_while_opcode, i = do_while_statement(tokens, i+1, table)
            op_codes.append(do_while_opcode)
        # Otherwise increment the index
        else:
            i += 1

    # Return opcodes
    return op_codes
