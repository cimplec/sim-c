# Library to take input as command line argument
import sys

# Module to import some helper functions
from global_helpers import error, is_alpha, is_alnum, is_digit

# Module to import Token class
from token_class import Token

def is_keyword(value):
    """
        Params
        ======
        value (string) = The string to be checked for keyword

        Returns
        =======
        Whether the value passed is a keyword or not
    """

    return value in ['print']

def numeric_val(source_code, i):
    """
        Params
        ======
        source_code (string) = The string containing simc source code
        i           (int)    = The current index in the source code

        Returns
        =======
        The token generated for the numeric constant and the current position in source code,
        this is done only if there is no error in the numeric constant
    """

    numeric_constant = ""

    # Loop until we get a non-digit character
    while(is_digit(source_code[i])):
        numeric_constant += source_code[i]
        i += 1

    # If a numeric constant contains more than 1 decimal point (.) then that is invalid
    if(numeric_constant.count('.') > 1):
        error('Invalid numeric constant, cannot have more than one decimal point in a number!')

    return Token("number", numeric_constant), i

def string_val(source_code, i):
    """
        Params
        ======
        source_code (string) = The string containing simc source code
        i           (int)    = The current index in the source code

        Returns
        =======
        The token generated for the string constant and the current position in source code,
        this is done only if there is no error in the string constant
    """

    string_constant = ""

    # Skip the first " so that the string atleast makes into the while loop
    i += 1

    # Loop until we get a non-digit character
    while(source_code[i] != '\"'):
        if(source_code[i] == '\0'):
            error('Unterminated string!')

        string_constant += source_code[i]
        i += 1

    # Skip the " character so that it does not loop back to this function incorrectly
    i += 1

    return Token("string", string_constant), i

def keyword_identifier(source_code, i):
    """
        Params
        ======
        source_code (string) = The string containing simc source code
        i           (int)    = The current index in the source code

        Returns
        =======
        The token generated for the keyword or identifier and the current position in source code
    """

    value = ""

    # Loop until we get a non-digit character
    while(is_alnum(source_code[i])):
        value += source_code[i]
        i += 1

    if is_keyword(value):
        return Token(value, ""), i

    return Token("id", value), i

def lexical_analyzer():
    """
        Returns
        ========
        A list of tokens of the source code, if the code is lexically correct, otherwise
        presents user with an error
    """

    # Get filename input as a command line argument
    filename = sys.argv[1]

    # Check if file extension is .simc or not
    if('.' not in filename or filename.split('.')[-1] != 'simc'):
        error('Incorrect file extension')

    # Read the entire source code as a string
    source_code = open(filename, 'r').read()
    source_code += '\0'

    tokens = []

    # Loop through the source code character by character
    i = 0
    while(source_code[i] != '\0'):
        # If a digit appears, call numeric_val function and add the numeric token to list,
        # if it was correct
        if is_digit(source_code[i]):
            token, i = numeric_val(source_code, i)
            tokens.append(token)
        elif source_code[i] == '\"':
            token, i = string_val(source_code, i)
            tokens.append(token)
        elif is_alnum(source_code[i]):
            token, i = keyword_identifier(source_code, i)
            tokens.append(token)
        elif source_code[i] == '(':
            tokens.append(Token("left_paren", ""))
            i += 1
        elif source_code[i] == ')':
            tokens.append(Token("right_paren", ""))
            i += 1
        else:
            i += 1

    return tokens

# Main
if __name__ == '__main__':
    # Call the lexical analyzer
    tokens = lexical_analyzer()

    # Print all the tokens
    for token in tokens:
        print(token)
