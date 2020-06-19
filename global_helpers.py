# Library to exit code when error occurs
import sys

def error(msg):
    """
        Params
        ======
        msg (string) = The message to be shown as error message
    """

    # Prints the error to screen in red color and then exits tokenizer
    print('\033[91mError: ' + msg)
    sys.exit()

def is_digit(char):
    """
        Params
        ======
        char (string) = Single character mostly part of a longer string

        Returns
        =======
        Checks whether the character is number or not, since '.' is not considered an alphabet by the
        standard isdigit function
    """

    return char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']

def is_alpha(char):
    """
        Params
        ======
        char (string) = Single character mostly part of a longer string

        Returns
        =======
        Checks whether the character is alphabet or not, since '_' is not considered a digit by the
        standard isalpha function
    """

    return char.isalpha() or char == '_'

def is_alnum(char):
    """
        Params
        ======
        char (string) = Single character mostly part of a longer string

        Returns
        =======
        Checks whether the character is alphabet/digit not, since '_' is not considered an alphabet by the
        isalpha function, and '.' is not considered a digit by the standard isdigit function
    """

    return char.isalpha() or char == '_' or char in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
