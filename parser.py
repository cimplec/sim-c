# Module to import some helper functions
from global_helpers import error

# Module to import OpCode class
from op_code import OpCode

def check_if(given_type, should_be_types, msg):
    """
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

def print_statement(tokens, i, table):
    """
        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token

        Returns
        =======
        The opcode for the current code and the index after parsing print statement

        Grammar
        =======
        print_statement -> print(expr)
        expr            -> string | number
        string          -> quote [a-zA-Z0-9`~!@#$%^&*()_-+={[]}:;,.?/|\]+ quote
        quote           -> "
        number          -> [0-9]+
    """

    # Check if ( follows print statement
    check_if(tokens[i].type, "left_paren", "Expected ( after print statement")

    # Check if string/number follows ( in print statement
    check_if(tokens[i+1].type, ["number", "string", "id"], "Expected expression inside print statement")

    # Check if print statement has closing )
    check_if(tokens[i+2].type, "right_paren", "Expected ) after expression in print statement")

    value, type, typedata = table.get_by_id(tokens[i+1].val)

    op_value = ""
    if(type == 'string'):
        op_value = value if typedata == 'constant' else '\"%s\", ' + value
    elif(type == 'char'):
        op_value = '\"%c\", ' + value
    elif(type == 'int'):
        op_value = '\"%d\", ' + str(value)
    elif(type == 'float'):
        op_value = '\"%f\", ' + str(value)
    elif(type == 'double'):
        op_value = '\"%lf\", ' + str(value)

    # Return the opcode and i+3 (the token after print statement)
    return OpCode("print", op_value), i+3

def var_statement(tokens, i, table):
    check_if(tokens[i].type, "id", "Expected id after var keyword")

    if(tokens[i+1].type == 'assignment'):
        if(tokens[i+2].type in ['number', 'string']):
            value, type, typedata = table.get_by_id(tokens[i+2].val)

            table.symbol_table[tokens[i].val][1] = type

            return OpCode("var_assign", table.symbol_table[tokens[i].val][0] + '---' + value, type), i+3

def parse(tokens, table):
    """
        Params
        ======
        tokens (list) = List of tokens

        Returns
        =======
        The list of opcodes

        Grammar
        =======
        statement -> print_statement
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
        # Otherwise increment the index
        else:
            i += 1

    # Return opcodes
    return op_codes
