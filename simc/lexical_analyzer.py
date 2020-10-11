# Standard library to take input as command line argument
import sys

# Module to import some helper functions
from .global_helpers import error, is_alpha, is_alnum, is_digit

# Module to import Token class
from .token_class import Token


def is_keyword(value):
    """
    Checks if string is keyword or not

    Params
    ======
    value (string) = The string to be checked for keyword

    Returns
    =======
    bool: Whether the value passed is a keyword or not
    """
    return value in [
        "fun",
        "do",
        "MAIN",
        "print",
        "return",
        "var",
        "END_MAIN",
        "for",
        "in",
        "to",
        "by",
        "while",
        "if",
        "else",
        "break",
        "continue",
        "input",
        "exit",
        "switch",
        "case",
        "default",
        "BEGIN_C",
        "END_C"
    ]


def numeric_val(source_code, i, table, line_num):
    """
    Processes numeric values in the source code

    Params
    ======
    source_code (string)      = The string containing simc source code
    i           (int)         = The current index in the source code
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    line_num    (int)         = Line number

    Returns
    =======
    Token, int: The token generated for the numeric constant and the current position in source code,
                this is done only if there is no error in the numeric constant
    """

    numeric_constant = ""

    # Loop until we get a non-digit character
    while is_digit(source_code[i]):
        numeric_constant += source_code[i]
        i += 1

    # If a numeric constant contains more than 1 decimal point (.) then that is invalid
    if numeric_constant.count(".") > 1:
        error(
            "Invalid numeric constant, cannot have more than one decimal point in a"
            " number!",
            line_num,
        )

    # Check the length after . to distinguish between float and double
    length = len(numeric_constant.split(".")[1]) if "." in numeric_constant else 0

    # Determine type of numeric value
    type = "int"
    if length != 0:
        if length <= 7:
            type = "float"
        elif length >= 7:
            type = "double"

    # Make entry in symbol table
    id = table.entry(numeric_constant, type, "constant")

    # Return number token and current index in source code
    return Token("number", id, line_num), i


def string_val(source_code, i, table, line_num, start_char='"'):
    """
    Processes string values in the source code

    Params
    ======
    source_code (string) = The string containing simc source code
    i           (int)    = The current index in the source code
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    line_num    (int)         = Line number
    start_char  (str) (Optional) = Character with which string starts

    Returns
    =======
    Token, int: The token generated for the string constant and the current position in source code,
                this is done only if there is no error in the string constant
    """

    string_constant = ""

    # Skip the first " so that the string atleast makes into the while loop
    i += 1

    # Loop until we get a non-digit character
    while source_code[i] != start_char:
        if source_code[i] == "\0":
            error("Unterminated string!", line_num)

        string_constant += source_code[i]
        i += 1

    # Skip the " character so that it does not loop back to this function incorrectly
    i += 1

    # Determine the type of data
    type = "char"
    escape_sequences  = ['\\\\','\\0','\\n','\\a','\\b','\\e',
                        '\\f','\\r','\\t','\\v','\\?']
    if len(string_constant) > 1 and string_constant not in escape_sequences:
        type = "string"

    # Put appropriate quote
    string_constant = (
        '"' + string_constant + '"' if type == "string" else "'" + string_constant + "'"
    )

    # Make entry in symbol table
    id = table.entry(string_constant, type, "constant")

    # Return string token and current index in source code
    return Token("string", id, line_num), i


def keyword_identifier(source_code, i, table, line_num):
    """
    Process keywords and identifiers in source code

    Params
    ======
    source_code (string) = The string containing simc source code
    i           (int)    = The current index in the source code
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    line_num    (int)         = Line number

    Returns
    =======
    Token, int: The token generated for the keyword or identifier and the current position in source code
    """

    value = ""

    # Loop until we get a non-digit character
    while is_alnum(source_code[i]):
        value += source_code[i]
        i += 1

    # Check if value is keyword or not
    if is_keyword(value):
        return Token(value, "", line_num), i

    # Check if identifier is in symbol table
    id = table.get_by_symbol(value)

    C_keywords = [
        "break",
        "else",
        "long",
        "switch",
        "case",
        "enum",
        "register",
        "typedef",
        "char",
        "extern",
        "return",
        "union",
        "const",
        "float",
        "short",
        "unsigned",
        "continue",
        "for",
        "signed",
        "void",
        "default",
        "goto",
        "sizeof",
        "volatile",
        "do",
        "if",
        "static",
        "while",
    ]

    # Check if identifier is a keyword in class
    if value in C_keywords:
        error("A keyword cannot be an identifier - %s" % value, line_num)

    # If identifier is not in symbol table then give a placeholder datatype var
    if id == -1:
        id = table.entry(value, "var", "variable")

    # Return id token and current index in source code
    return Token("id", id, line_num), i


def get_raw_tokens(source_code,i,line_num):
    """
    makes tokens of each line in C, written between BEGIN_C and END_C

    Params
    ======
    source_code (string) = The string containing simc source code
    i           (int)    = The current index in the source code
    line_num    (int)         = Line number

    Returns
    =======
    [Token], int,int: List of raw tokens, current place in source_code, current line_number in source_code
    """

    #keep line_num to show in case of error
    begin = line_num
    tokens = []
    while True :
        val = ""

        # capture whole line        
        while source_code[i] != "\n" and source_code[i] != "\0" :
            val += source_code[i]
            i += 1

        # if END_C found, add 1 to account for newline, and return
        if val.strip() == "END_C":
            i += 1
            line_num += 1
            return tokens,i,line_num

        elif source_code[i] == "\0":
            error("No matching END_C found to BEGIN_C",begin)
        else:
            tokens.append(Token("RAW_C",val,line_num))

        # increment i and line_num to go to next line
        i += 1
        line_num += 1

def lexical_analyze(filename, table):
    """
    Generate tokens from source code

    Params
    ======
    filename    (string)      = The string containing simc source code filename
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants

    Returns
    ========
    list: A list of tokens of the source code, if the code is lexically correct, otherwise
          presents user with an error
    """

    # Line number
    line_num = 1

    # Read the entire source code as a string
    source_code = open(filename, "r").read()
    source_code += "\0"

    # List of tokens
    tokens = []

    # Parantheses checker for detecting function call
    parantheses_count = 0

    # To store comment string
    comment_str = ""

    # To indicate if BEGIN_C has been encountered
    raw_c = False

    # Loop through the source code character by character
    i = 0
    while source_code[i] != "\0":

        # If we have encountered BEGIN_C, copy everything exactly same until END_C
        if raw_c :
            raw_tokens,i,line_num = get_raw_tokens(source_code,i,line_num)
            tokens.extend(raw_tokens)
            raw_c = False
            
        # If a digit appears, call numeric_val function and add the numeric token to list,
        # if it was correct
        if is_digit(source_code[i]):
            token, i = numeric_val(source_code, i, table, line_num)
            tokens.append(token)

        # If double quote appears the value is a string token
        elif source_code[i] == '"':
            token, i = string_val(source_code, i, table, line_num)
            tokens.append(token)

        # If single quote appears the value is a string token
        elif source_code[i] == "'":
            token, i = string_val(source_code, i, table, line_num, start_char="'")
            tokens.append(token)

        # If alphabet or number appears then it might be either a keyword or an identifier
        elif is_alnum(source_code[i]):
            token, i = keyword_identifier(source_code, i, table, line_num)
            if token.type == "BEGIN_C":
                raw_c = True
                continue
            elif token.type == "END_C":
                raw_c = False
                continue
            tokens.append(token)

        # Identifying left paren token
        elif source_code[i] == "(":
            if tokens[-1].type == "id" or parantheses_count > 0:
                parantheses_count += 1
            tokens.append(Token("left_paren", "", line_num))
            i += 1

        # Identifying right paren token
        elif source_code[i] == ")":
            if parantheses_count > 0:
                parantheses_count -= 1

            tokens.append(Token("right_paren", "", line_num))

            if parantheses_count == 0:
                tokens.append(Token("call_end", "", line_num))

            i += 1

        # Identifying left brace token
        elif source_code[i] == "{":
            tokens.append(Token("left_brace", "", line_num))
            i += 1

        # Identifying right brace token
        elif source_code[i] == "}":
            tokens.append(Token("right_brace", "", line_num))
            i += 1

        # Identifying newline token
        elif source_code[i] == "\n":
            tokens.append(Token("newline", "", line_num))
            line_num += 1
            i += 1

        # Identifying assignment token or equivalence token
        elif source_code[i] == "=":
            if source_code[i + 1] != "=":
                tokens.append(Token("assignment", "", line_num))
                i += 1
            else:
                tokens.append(Token("equal", "", line_num))
                i += 2

        # Identifying plus_equal, increment or plus token
        elif source_code[i] == "+":
            if source_code[i + 1] == "=":
                tokens.append(Token("plus_equal", "", line_num))
                i += 2
            elif source_code[i + 1] == "+":
                tokens.append(Token("increment", "", line_num))
                i += 2
            else:
                tokens.append(Token("plus", "", line_num))
                i += 1

        # Identifying minus_equal, decrement or minus token
        elif source_code[i] == "-":
            if source_code[i + 1] == "=":
                tokens.append(Token("minus_equal", "", line_num))
                i += 2
            elif source_code[i + 1] == "-":
                tokens.append(Token("decrement", "", line_num))
                i += 2
            else:
                tokens.append(Token("minus", "", line_num))
                i += 1

        # Identifying multiply_equal or multiply token
        elif source_code[i] == "*":
            if source_code[i + 1] == "=":
                tokens.append(Token("multiply_equal", "", line_num))
                i += 2
            else:
                tokens.append(Token("multiply", "", line_num))
                i += 1

        # Identifying or power token
        elif source_code[i] == "^":
            tokens.append(Token("power", "", line_num))
            i += 1

        # Identifying 'address of' token
        elif source_code[i] == "&":
            tokens.append(Token("address_of", "", line_num))
            i += 1

        # Identifying divide_equal or divide token
        elif source_code[i] == "/":
            if source_code[i + 1] == "=":
                tokens.append(Token("divide_equal", "", line_num))
                i += 2
            # to check if it is a single line comment
            elif source_code[i + 1] == "/":
                i += 2
                while source_code[i] != "\n":
                    comment_str += str(source_code[i])
                    i += 1
                tokens.append(Token("single_line_comment", comment_str, line_num))
                comment_str = ""
            # to check if it is a multi line comment
            elif source_code[i + 1] == "*":
                i += 2
                while source_code[i] != "*" and source_code[i + 1] != "/":
                    comment_str += str(source_code[i])
                    i += 1
                tokens.append(Token("multi_line_comment", comment_str, line_num))
                comment_str = ""
            else:
                tokens.append(Token("divide", "", line_num))
                i += 1

        # Identifying modulus_equal or modulus token
        elif source_code[i] == "%":
            if source_code[i + 1] == "=":
                tokens.append(Token("modulus_equal", "", line_num))
                i += 2
            else:
                tokens.append(Token("modulus", "", line_num))
                i += 1

        # Identifying comma token
        elif source_code[i] == ",":
            tokens.append(Token("comma", "", line_num))
            i += 1

        # Identifying not_equal token
        elif source_code[i] == "!" and source_code[i + 1] == "=":
            tokens.append(Token("not_equal", "", line_num))
            i += 2

        # Identifying greater_than or greater_than_equal token
        elif source_code[i] == ">":
            if source_code[i + 1] not in ["=", ">"]:
                tokens.append(Token("greater_than", "", line_num))
                i += 1
            elif source_code[i + 1] == "=":
                tokens.append(Token("greater_than_equal", "", line_num))
                i += 2
            else:
                tokens.append(Token("right_shift", "", line_num))
                i += 2

        # Identifying less_than or less_than_equal token
        elif source_code[i] == "<":
            if source_code[i + 1] not in ["<", "="]:
                tokens.append(Token("less_than", "", line_num))
                i += 1
            elif source_code[i + 1] == "=":
                tokens.append(Token("less_than_equal", "", line_num))
                i += 2
            elif source_code[i + 1] == "<":
                tokens.append(Token("left_shift", "", line_num))
                i += 2

        # Identifiying colon token
        elif source_code[i] == ":":
            tokens.append(Token("colon", "", line_num))
            i += 1

        # Otherwise increment the index
        else:
            i += 1

    # Return the generated tokens
    return tokens
