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

def expression(tokens, i, table, msg):
    """
        Parse and expression from tokens

        Params
        ======
        tokens      (list)        = List of tokens
        i           (string/list) = Current index in list of tokens
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
        msg         (string)      = Error message to print in case some case fails

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
    while(tokens[i].type in ['number', 'string', 'id', 'plus', 'minus', 'multiply', 'divide', 'input', 'left_paren', 'right_paren', 'comma']):
        # If token is identifier or constant
        if(tokens[i].type in ['number', 'string', 'id']):
            # Fetch information from symbol table
            value, type, typedata = table.get_by_id(tokens[i].val)

            if(type == 'string'):
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
            elif(type == 'var'):
                error("Cannot find the type of %s" % value)
        else:
            if(tokens[i].type == 'plus'):
                op_value += ' + '
            elif(tokens[i].type == 'minus'):
                op_value += ' - '
            elif(tokens[i].type == 'multiply'):
                op_value += ' * '
            elif(tokens[i].type == 'divide'):
                op_value += ' / '
            elif(tokens[i].type == 'input'):
                op_value += ' scanf '


        i += 1

    # If expression is empty then throw an error
    if(op_value == ""):
        error(msg)

    #Check if statement is of type input
    if ' scanf ' in op_value:
        #Check if there exists a prompt message
        if('"' in op_value):
            i1 = op_value.index('"')+1
            i2 = op_value.index('"',i1)
            #Extracting the prompt
            msg = op_value[i1:i2]
            #Checking if dtype is mentioned
            if('\'' in op_value[i2+1:]):
                i1 = op_value.index('\'',i2+1)+1
                i2 = op_value.index('\'',i1)
                dtype = op_value[i1:i2]
            else:
                #default dtype is string
                dtype = 's'
        else:
            msg = ""
            dtype = 's'
        dtype_to_prec = {'i': 3, 'f': 4, 'd': 5, 's': 1}
        op_value = str(msg)+'---'+str(dtype)
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
        OpCode, int: The opcode for the var_assign/var_no_assign code and the index after parsing print statement

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
        #Check if the statement is of the type input

        # Return the opcode and i (the token after var statement
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
        OpCode, int: The opcode for the assign code and the index after parsing print statement

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
    check_if(tokens[i].type, "assignment", "Expected assignment operator after identifier")

    # Store the index of identifier
    id_idx = i-1

    # Check if expression follows = in assign statement
    op_value, op_type, i = expression(tokens, i+1, table, "Required expression after assignment operator")

    #  Map datatype to appropriate datatype in C
    prec_to_type = {0: "string", 1: "string", 2: "char", 3: "int", 4: "float", 5: "double"}

    # Modify datatype of the identifier
    table.symbol_table[tokens[id_idx].val][1] = prec_to_type[op_type]
    #Check if the statement is of the type input

    return OpCode("assign", table.symbol_table[tokens[id_idx].val][0] + '---' + op_value, ""), i

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
        statement -> print_statement | var_statement | assign_statement
    """

    # List of opcodes
    op_codes = []

    # Loop through all the tokens
    i = 0
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
            assign_opcode, i = assign_statement(tokens, i+1, table)
            op_codes.append(assign_opcode)
        # Otherwise increment the index
        else:
            i += 1

    # Return opcodes
    return op_codes
