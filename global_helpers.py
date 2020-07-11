# Library to exit code when error occurs
import sys


def error(msg, line_num):
    """
    Shows error message in red color and exits the current process

    Params
    ======
    msg      (string) = The message to be shown as error message
    line_num (int)         = Line number
    """

    # Prints the error to screen in red color and then exits tokenizer
    print("\033[91m[Line %d] Error: %s" % (line_num, msg))
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
