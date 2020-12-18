# Library to exit code when error occurs
import sys


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

def check_incomplete(i, tokens, msg, line_num):
    if i == len(tokens):
        error(msg, line_num)

def error(msg, line_num):
    """
    Shows error message in red color and exits the current process

    Params
    ======
    msg      (string) = The message to be shown as error message
    line_num (int)         = Line number
    """

    # Prints the error to screen in red color and then exits tokenizer
    print("\033[91m[Line %d] Error: %s" % (line_num, msg), end=" ")
    print(" \033[m")
    sys.exit()


def is_digit(char):
    """
    Checks if character is digit or not

    Params
    ======
    char (string) = Single character mostly part of a longer string

    Returns
    =======
    bool: Checks whether the character is number or not, since '.' is not considered an alphabet by the
          standard isdigit function
    """

    return char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]


def is_alpha(char):
    """
    Checks if character is alphabet or not

    Params
    ======
    char (string) = Single character mostly part of a longer string

    Returns
    =======
    bool: Checks whether the character is alphabet or not, since '_' is not considered a digit by the
          standard isalpha function
    """

    return char.isalpha() or char == "_"


def is_alnum(char):
    """
    Checks if character is alphabet or digit or none

    Params
    ======
    char (string) = Single character mostly part of a longer string

    Returns
    =======
    bool: Checks whether the character is alphabet/digit not, since '_' is not considered an alphabet by the
          isalpha function, and '.' is not considered a digit by the standard isdigit function
    """

    return (
        char.isalpha()
        or char == "_"
        or char in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."]
    )
