# Library to take input as command line argument
import sys

class Token():
    """
        Token class is responsible for creating tokens
    """

    def __init__(self, type, val):
        """
            Class initializer

            Params
            ======
            type     (string) = type of token as string
            typedig  (int)    = type of token as integer
            val      (string) = value stored at token
        """

        self.type = type
        self.typedig = self.token2dig(type)
        self.val = val

    def __str__(self):
        """
            Returns
            =======
            The string representation of token class, which can be used to print the tokens
        """

        return "Token(%s, %s)" % (self.type, self.val)

    def token2dig(self, str_type):
        """
            Params
            ======
            str_type (string) = String representation of token type

            Returns
            =======
            The integer representation of the string token
        """

        dic = {"number": 1, "string": 2, "print": 3}
        return dic.get(str_type, 0)

def is_digit(char):
    """
        Params
        ======
        char (string) = Single character mostly part of a longer string

        Returns
        =======
        Checks whether the character is number or not, since '.' is not considered a digit by the
        standard isdigit function
    """

    if char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']:
        return True
    return False

def error(msg):
    """
        Params
        ======
        msg (string) = The message to be shown as error message
    """

    # Prints the error to screen in red color and then exits tokenizer
    print('\033[91mError: ' + msg)
    sys.exit()

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
