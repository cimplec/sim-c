# Standard library to take input as command line argument
import sys
import os
from collections import namedtuple

# Module to import some helper functions
from .global_helpers import error, is_alpha, is_alnum, is_digit

# Module to import Token class
from .token_class import Token


class LexicalAnalyzer:
    """
    Lexical analyzer class is responsible for performing lexical analysis and generating tokens
    """

    def __init__(self, source_filename, symbol_table):
        """
        Class initializer

        Params
        ======
        source_filename (string)                        = Name of file containing sim-C source code
        symbol_table    (simc.symbol_table.SymbolTable) = Shared symbol table
        """

        self.source_filename = source_filename
        self.symbol_table = symbol_table

        self.common_simc_c_keywords = [
            "break",
            "case",
            "continue",
            "default",
            "do",
            "else",
            "for",
            "if",
            "return",
            "struct",
            "switch",
            "while",
        ]

        self.simc_unique_keywords = [
            "BEGIN_C",
            "END_C",
            "END_MAIN",
            "MAIN",
            "by",
            "exit",
            "false",
            "fun",
            "import",
            "in",
            "input",
            "print",
            "to",
            "true",
            "var",
            "size",
            "type",
        ]

        self.c_unique_keywords = [
            "auto",
            "char",
            "const",
            "double",
            "enum",
            "extern",
            "float",
            "goto",
            "int",
            "long",
            "register",
            "short",
            "signed",
            "sizeof",
            "static",
            "typedef",
            "union",
            "unsigned",
            "void",
            "volatile",
        ]

    def __read_source_code(self):
        """
        Read source code from source file path and return it in a string

        Returns
        =======
        str: sim-C source code
        """

        # Open file and read sim-C source code
        source_code = ""
        with open(self.source_filename, "r") as file:
            source_code = file.read()

        # Add end of string character to indicate end of source code
        source_code += "\0"

        return source_code

    def update_filename(self, source_filename):
        """
        Update sim-C source file path, used during lexical analysis of module sources
        """

        self.source_filename = source_filename

    def __update_source_index(self, by=1):
        """
        Update current source index by an integer
        """

        self.current_source_index += by

    def __check_next_token(self, next_chars, tokens_if_true, token_if_false):
        """
        Generates token based on value of next token

        Params
        ======
        next_chars      (list) = Characters to be checked in the next index
        tokens_if_true  (list) = Corresponding tokens to be generated based on which character matches
        tokens_if_false (str)  = Token to be generated if none of these characters succeeds the current character
        """

        # Loop through all next characters and corresponding tokens if they match
        for next_char, token_if_true in zip(next_chars, tokens_if_true):

            # If there is a match append to tokens and return
            if self.source_code[self.current_source_index + 1] == next_char:
                self.tokens.append(Token(token_if_true, "", self.line_num))
                self.__update_source_index(by=2)
                return

        # If none of the characters match then generate the token of type token_if_false
        self.tokens.append(Token(token_if_false, "", self.line_num))
        self.__update_source_index()

    def __initialize_flags_counters(self):
        """
        Initialize flags and counter variables used for lexical analysis
        """

        # Line number
        self.line_num = 1

        # Parantheses checker for detecting function call
        self.parantheses_count = 0

        # To store comment string
        self.comment_str = ""

        # Directory where installed modules can be found
        self.module_dir = os.path.join(os.path.dirname(__file__), "modules")

        # Path to source code of all the modules
        self.module_source_paths = []

        # To indicate if BEGIN_C has been encountered
        self.raw_c_begin = False

        # Flag to check whether id is a module name or a normal id, this is set to true whenever an import is encountered
        self.is_id_module_name = False

        # Stores whether we got a number or variable just before this index
        # This is to presently differentiate between bitwise and
        # and address of operations
        self.got_num_or_var = False

        # To check if the brackets are balanced:
        self.top = -1
        self.balanced_brackets_stack = []

    def __is_keyword(self, value):
        """
        Checks if string is keyword or not

        Params
        ======
        value (string) = The string to be checked for keyword

        Returns
        =======
        bool: Whether the value passed is a keyword or not
        """

        return value in (self.common_simc_c_keywords + self.simc_unique_keywords)

    def __numeric_val(self):
        """
        Processes numeric values in the source code
        """

        numeric_constant = ""

        # Loop until we get a non-digit character
        while is_digit(self.source_code[self.current_source_index]):
            numeric_constant += self.source_code[self.current_source_index]
            self.__update_source_index()

        # If a numeric constant contains more than 1 decimal point (.) then that is invalid
        if numeric_constant.count(".") > 1:
            error(
                "Invalid numeric constant, cannot have more than one decimal point in a"
                " number!",
                self.line_num,
            )

        # Check the length after . to distinguish between float and double
        length_after_decimal = (
            len(numeric_constant.split(".")[1]) if "." in numeric_constant else 0
        )

        # Determine type of numeric value
        type_ = "int"
        if length_after_decimal != 0:
            if length_after_decimal <= 7:
                type_ = "float"
            elif length_after_decimal >= 7:
                type_ = "double"

        # Make entry in symbol table
        id_ = self.symbol_table.entry(numeric_constant, type_, "constant")

        # Return number token and current index in source code
        self.tokens.append(Token("number", id_, self.line_num))

    def __string_val(self, start_char='"'):
        """
        Processes string values in the source code
        """

        # Temporary buffer to save string contents
        string_constant = ""

        # Skip the first " or ' so that the string atleast makes into the while loop
        self.__update_source_index()

        # Loop until " or ' is matched (with whichever it started)
        while (self.current_source_index < len(self.source_code)) and (
            self.source_code[self.current_source_index] != start_char
        ):
            # If we reach the end of source code then the string is unterminated
            if self.source_code[self.current_source_index] in ["\0", "\n"]:
                error("Unterminated string", self.line_num)

            # Process \" and \' escape sequences
            if (
                self.source_code[self.current_source_index] == f"\\"
                and self.source_code[self.current_source_index + 1] == start_char
            ):
                string_constant += (
                    self.source_code[self.current_source_index]
                    + self.source_code[self.current_source_index + 1]
                )
                self.__update_source_index(by=2)
            else:
                string_constant += self.source_code[self.current_source_index]
                self.__update_source_index()

        # If we reached end of source code without terminating string then it is unterminated
        if self.current_source_index == len(self.source_code):
            error("Unterminated string", self.line_num)

        # Skip the " or ' character so that it does not loop back to this function incorrectly
        self.__update_source_index()

        # Determine the type of data
        type_ = "char"

        escape_sequences = [
            "\\\\",
            "\\0",
            "\\n",
            "\\a",
            "\\b",
            "\\f",
            "\\r",
            "\\t",
            "\\v",
            "\\?",
            "\\'",
            '\\"',
        ]

        if len(string_constant) > 1 and string_constant not in escape_sequences:
            type_ = "string"

        # Put appropriate quote
        string_constant = (
            '"' + string_constant + '"'
            if type_ == "string"
            else "'" + string_constant + "'"
        )

        # Make entry in symbol table
        id_ = self.symbol_table.entry(string_constant, type_, "constant")

        # Return string token and current index in source code
        self.tokens.append(Token("string", id_, self.line_num))

    def __keyword_identifier(self):
        """
        Process keywords and identifiers in source code
        """

        # Temporary buffer to hold identifier name
        value = ""

        # Loop until we get a non-alphanumeric character
        while is_alnum(self.source_code[self.current_source_index]):
            value += self.source_code[self.current_source_index]
            self.__update_source_index()

        # Check if value (name of type) is valid or not
        allowed_dtypes_for_casting = ["int", "float", "double"]

        # Check if next character is (, then it can possibly be explicit typecasting
        allow_c_keyword = False
        if self.source_code[self.current_source_index] == "(" and value in allowed_dtypes_for_casting:
            allow_c_keyword = True
        
        # For generating bool or math constant type tokens
        types = namedtuple("types", ["data_type", "token_type"])
        const_with_types = {
            "true": types("bool", "bool"),
            "false": types("bool", "bool"),
            "PI": types("double", "number"),
            "E": types("double", "number"),
            "inf": types("double", "number"),
            "NaN": types("double", "number"),
        }

        # Handle boolean and math constants
        if value in const_with_types.keys():
            id_ = self.symbol_table.entry(
                value, const_with_types[value].data_type, "constant"
            )
            self.tokens.append(
                Token(const_with_types[value].token_type, id_, self.line_num)
            )
            return

        # Check if value is keyword or not
        elif self.__is_keyword(value):
            self.tokens.append(Token(value, "", self.line_num))
            return

        C_keywords = self.c_unique_keywords + self.common_simc_c_keywords

        # If this flag is true then we won't throw error when C keyword is used as id
        # This helps in case of explicit type casting
        if allow_c_keyword:
            self.tokens.append(Token("type_cast", value, self.line_num))
            return
        else:
            if value in C_keywords:
                error("A keyword cannot be an identifier - %s" % value, self.line_num)

        # Check if identifier is in symbol self.symbol_table
        id_ = self.symbol_table.get_by_symbol(value)

        # If identifier is not in symbol self.symbol_table then give a placeholder datatype var
        if id_ == -1:
            id_ = self.symbol_table.entry(value, "var", "variable")

        # Return id token and current index in source code
        self.tokens.append(Token("id", id_, self.line_num))

    def __get_raw_tokens(self):
        """
        Makes RAW_C tokens for each line of C code written between BEGIN_C and END_C
        """

        while True:
            raw_c_code = ""

            # Loop until end of line
            while self.source_code[self.current_source_index] not in ["\n", "\0"]:
                raw_c_code += self.source_code[self.current_source_index]
                self.__update_source_index()

            # If END_C found, add 1 to account for newline, and return
            if raw_c_code.strip() == "END_C":
                self.__update_source_index()
                self.line_num += 1
                return
            elif self.source_code[self.current_source_index] == "\0":
                error("No matching END_C found to BEGIN_C", self.line_num)
            else:
                self.tokens.append(Token("RAW_C", raw_c_code, self.line_num))

            # increment self.current_source_index and self.line_num to go to next line
            self.__update_source_index()
            self.line_num += 1

    def lexical_analyze(self):
        """
        Generate tokens from source code

        Returns
        ========
        list: A list of tokens of the source code, if the code is lexically correct
        list: A list of module source paths
        """

        # Read source code from file, initialize flags and counters
        self.source_code = self.__read_source_code()
        self.current_source_index = 0

        self.__initialize_flags_counters()

        self.tokens = []

        # Loop until end of source code
        while self.source_code[self.current_source_index] != "\0":

            # This is set to true only if number or variable is found
            self.got_num_or_var = False if self.got_num_or_var != True else True

            # If we have encountered BEGIN_C, copy everything exactly same until END_C
            if self.raw_c_begin:
                self.__get_raw_tokens()
                self.raw_c_begin = False

            # If a digit appears, call numeric_val function and add the numeric token to list
            if is_digit(self.source_code[self.current_source_index]):
                self.__numeric_val()
                self.got_num_or_var = True

            # If double quote appears the value is a string token
            elif self.source_code[self.current_source_index] == '"':
                self.__string_val()

            # If single quote appears the value is a string token
            elif self.source_code[self.current_source_index] == "'":
                self.__string_val(start_char="'")

            # If alphabet or number appears then it might be either a keyword or an identifier
            elif is_alnum(self.source_code[self.current_source_index]):
                self.__keyword_identifier()

                # If token is an id it might be name of a module
                if self.tokens[-1].type == "id":
                    self.got_num_or_var = True

                    if self.is_id_module_name:
                        # Switch off the flag
                        self.is_id_module_name = not self.is_id_module_name

                        # Get name of module from symbol table
                        module_name, _, _, _ = self.symbol_table.get_by_id(
                            self.tokens[-1].val
                        )

                        module_path = os.path.join(
                            self.module_dir, module_name + ".simc"
                        )

                        # Check if module is installed
                        if os.path.exists(module_path):
                            self.module_source_paths.append(module_path)
                        else:
                            error(
                                "Module "
                                + str(module_name)
                                + " not found, install it before using",
                                self.line_num,
                            )

                elif self.tokens[-1].type == "BEGIN_C":
                    self.raw_c_begin = True
                    continue
                elif self.tokens[-1].type == "END_C":
                    self.raw_c_begin = False
                    continue
                elif self.tokens[-1].type == "import":
                    self.is_id_module_name = True

            # Identifying left paren token
            elif self.source_code[self.current_source_index] == "(":
                # To check if parantheses are balanced:
                self.top += 1
                self.balanced_brackets_stack.append("(")

                self.parantheses_count += 1
                self.tokens.append(Token("left_paren", "", self.line_num))
                self.__update_source_index()

            # Identifying right paren token
            elif self.source_code[self.current_source_index] == ")":
                # To check if parantheses are balanced:
                if self.top == -1:
                    # If at any time there is underflow, there are too many closing parantheses.
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]
                    error("Too many closing parentheses", self.line_num)
                elif self.balanced_brackets_stack[self.top] != "(":
                    error("Unbalanced parentheses error", self.line_num)
                else:
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]

                if self.parantheses_count > 0:
                    self.parantheses_count -= 1
                    self.tokens.append(Token("right_paren", "", self.line_num))

                    # Read spaces between next code
                    while self.source_code[self.current_source_index + 1] is " ":
                        self.__update_source_index()

                    # Add call_end at end of an expression, which is detected as ")" followed by end line or "{"
                    if self.source_code[self.current_source_index + 1] in [
                        "\n",
                        "{",
                        "}",
                        ",",
                    ]:
                        self.tokens.append(Token("call_end", "", self.line_num))

                else:
                    error("Parentheses does not match", self.line_num)

                self.__update_source_index()

            # Identifying end of expression
            elif self.source_code[self.current_source_index] == "\n":
                if self.parantheses_count == 0:
                    self.tokens.append(Token("newline", "", self.line_num))
                else:
                    error("Parentheses does not match.", self.line_num)

                self.__update_source_index()
                self.line_num += 1

            # Identifying left brace token
            elif self.source_code[self.current_source_index] == "{":
                # To check if braces are balanced
                self.top += 1
                self.balanced_brackets_stack.append("{")

                self.tokens.append(Token("left_brace", "", self.line_num))
                self.__update_source_index()

            # Identifying right brace token
            elif self.source_code[self.current_source_index] == "}":
                # To check if braces are balanced:
                if self.top == -1:
                    # If at any time there is underflow, there are too many closing braces.
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]
                    error("Too many closing braces", self.line_num)
                elif self.balanced_brackets_stack[self.top] != "{":
                    error("Unbalanced braces error", self.line_num)

                else:
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]

                self.tokens.append(Token("right_brace", "", self.line_num))
                self.__update_source_index()

            # Identifying left bracket token
            elif self.source_code[self.current_source_index] == "[":
                # To check if brackets are balanced:
                self.top += 1
                self.balanced_brackets_stack.append("[")

                self.tokens.append(Token("left_bracket", "", self.line_num))
                self.__update_source_index()

            # Identifying right bracket token
            elif self.source_code[self.current_source_index] == "]":
                # To check if brackets are balanced:
                if self.top == -1:
                    # If at any time there is underflow, there are too many closing brackets.
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]
                    error("Too many closing brackets", self.line_num)
                elif self.balanced_brackets_stack[self.top] != "[":
                    error("Unbalanced brackets error", self.line_num)

                else:
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]
                
                self.tokens.append(Token("right_bracket", "", self.line_num))
                self.__update_source_index()

            # Identifying assignment token or equivalence token
            elif self.source_code[self.current_source_index] == "=":
                self.__check_next_token(["="], ["equal"], "assignment")

            # Identifying plus_equal, increment or plus token
            elif self.source_code[self.current_source_index] == "+":
                self.__check_next_token(["=", "+"], ["plus_equal", "increment"], "plus")

            # Identifying minus_equal, decrement or minus token
            elif self.source_code[self.current_source_index] == "-":
                self.__check_next_token(
                    ["=", "-"], ["minus_equal", "decrement"], "minus"
                )

            # Identifying multiply_equal, power or multiply token
            elif self.source_code[self.current_source_index] == "*":
                self.__check_next_token(
                    ["=", "*"], ["multiply_equal", "power"], "multiply"
                )

            # Identifying bitwise xor equal or bitwise xor token
            elif self.source_code[self.current_source_index] == "^":
                self.__check_next_token(["="], ["bitwise_xor_equal"], "bitwise_xor")

            # Identifying address of, and, or bitwise and token
            elif self.source_code[self.current_source_index] == "&":
                if self.source_code[self.current_source_index + 1] == "&":
                    self.tokens.append(Token("and", "", self.line_num))
                    self.__update_source_index(by=2)
                else:
                    if self.got_num_or_var:
                        self.__check_next_token(
                            ["="], ["bitwise_and_equal"], "bitwise_and"
                        )
                    else:
                        self.tokens.append(Token("address_of", "", self.line_num))
                        self.__update_source_index()

            # Identifying or token
            elif self.source_code[self.current_source_index] == "|":
                self.__check_next_token(
                    ["|", "="], ["or", "bitwise_or_equal"], "bitwise_or"
                )

            # Identifying divide_equal, single line comments, multi line comments, or divide token
            elif self.source_code[self.current_source_index] == "/":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("divide_equal", "", self.line_num))
                    self.__update_source_index(by=2)
                # to check if it is a single line comment
                elif self.source_code[self.current_source_index + 1] == "/":
                    self.__update_source_index(by=2)
                    while self.source_code[self.current_source_index] != "\n":
                        self.comment_str += str(
                            self.source_code[self.current_source_index]
                        )
                        self.__update_source_index()
                    self.tokens.append(
                        Token("single_line_comment", self.comment_str, self.line_num)
                    )
                    self.comment_str = ""
                # to check if it is a multi line comment
                elif self.source_code[self.current_source_index + 1] == "*":
                    self.__update_source_index(by=2)
                    while (
                        self.source_code[
                            self.current_source_index : self.current_source_index + 2
                        ]
                        != "*/"
                    ):
                        if self.source_code[self.current_source_index] == "\n":
                            self.line_num += 1
                        self.comment_str += str(
                            self.source_code[self.current_source_index]
                        )
                        self.__update_source_index()
                    self.__update_source_index(by=2)
                    self.tokens.append(
                        Token("multi_line_comment", self.comment_str, self.line_num)
                    )
                    self.comment_str = ""
                else:
                    self.tokens.append(Token("divide", "", self.line_num))
                    self.__update_source_index()

            # Identifying modulus_equal or modulus token
            elif self.source_code[self.current_source_index] == "%":
                self.__check_next_token(["="], ["modulus_equal"], "modulus")

            # Identifying comma token
            elif self.source_code[self.current_source_index] == ",":
                self.tokens.append(Token("comma", "", self.line_num))
                self.__update_source_index()
                
            # Identifying not_equal token
            elif (
                self.source_code[self.current_source_index] == "!"
                and self.source_code[self.current_source_index + 1] == "="
            ):
                self.tokens.append(Token("not_equal", "", self.line_num))
                self.__update_source_index(by=2)

            # Identifying greater_than or greater_than_equal token
            elif self.source_code[self.current_source_index] == ">":
                self.__check_next_token(
                    [">", "="], ["right_shift", "greater_than_equal"], "greater_than"
                )

            # Identifying less_than or less_than_equal token
            elif self.source_code[self.current_source_index] == "<":
                self.__check_next_token(
                    ["<", "="], ["left_shift", "less_than_equal"], "less_than"
                )

            # Identifiying colon token
            elif self.source_code[self.current_source_index] == ":":
                self.tokens.append(Token("colon", "", self.line_num))
                self.__update_source_index()

            # Otherwise increment the index
            else:
                self.__update_source_index()

        # By the end, if stack is not empty, there are extra opening brackets
        if self.top != -1:
            error("Unbalanced parentheses/braces/brackets error", self.line_num)

        # Return the generated tokens and module source paths
        return self.tokens, self.module_source_paths
