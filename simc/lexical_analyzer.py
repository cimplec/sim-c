# Standard library to take input as command line argument
import sys
import os

# Module to import some helper functions
from .global_helpers import error, is_alpha, is_alnum, is_digit

# Module to import Token class
from .token_class import Token

class LexicalAnalyzer:

    def __init__(self, filename, table):
        self.filename = filename 
        self.table = table

        self.common_simc_c_keywords = [
            'break', 'case', 'continue', 'default', 'do', 'else', 'for', 'if', 'return', 'struct', 'switch', 'while'
        ]

        self.simc_unique_keywords = [
            'BEGIN_C', 'END_C', 'END_MAIN', 'MAIN', 'by', 'exit', 'false', 'fun', 'import', 'in', 
            'input', 'print', 'to', 'true', 'var'
        ]

        self.c_unique_keywords = [
            'auto', 'char', 'const', 'double', 'enum', 'extern', 'float', 'goto', 'int', 'long', 'register', 
            'short', 'signed', 'sizeof', 'static', 'typedef', 'union', 'unsigned', 'void', 'volatile'
        ]

    def read_source_code(self):
        source = ""
        with open(self.filename, "r") as file:
            source = file.read()
        
        source += "\0"
        return source

    def update_filename(self, filename):
        self.filename = filename

    def initialize_flags_counters(self):
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
        self.raw_c = False

        # Flag to check whether id is a module name or a normal id, this is set to true whenever an import is encountered
        self.is_id_module_name = False

        # Stores whether we got a number or variable just before this index
        # This is to presently differentiate between bitwise and
        # and address of operations.
        self.got_num_or_var = False

        # To check if the brackets are balanced:
        self.top = -1
        self.balanced_brackets_stack = []

    def is_keyword(self, value):
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


    def numeric_val(self):
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
        while is_digit(self.source_code[self.current_source_index]):
            numeric_constant += self.source_code[self.current_source_index]
            self.current_source_index += 1

        # If a numeric constant contains more than 1 decimal point (.) then that is invalid
        if numeric_constant.count(".") > 1:
            error(
                "Invalid numeric constant, cannot have more than one decimal point in a"
                " number!",
                self.line_num,
            )

        # Check the length after . to distinguish between float and double
        length = len(numeric_constant.split(".")[1]) if "." in numeric_constant else 0

        # Determine type of numeric value
        type_ = "int"
        if length != 0:
            if length <= 7:
                type_ = "float"
            elif length >= 7:
                type_ = "double"

        # Make entry in symbol table
        id_ = self.table.entry(numeric_constant, type_, "constant")

        # Return number token and current index in source code
        self.tokens.append(Token("number", id_, self.line_num))


    def string_val(self, start_char='"'):
        """
        Processes string values in the source code

        Params
        ======
        source_code (string) = The string containing simc source code
        self.current_source_index           (int)    = The current index in the source code
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
        self.current_source_index += 1

        # Loop until we get a non-digit character
        if start_char == "'":
            if self.source_code[self.current_source_index] == "\\" and self.source_code[self.current_source_index + 1] == "'":
                string_constant += self.source_code[self.current_source_index] + self.source_code[self.current_source_index + 1]
                if self.source_code[self.current_source_index + 2] != start_char:
                    error("Unterminated string from here!", self.line_num)
                self.current_source_index += 2
            else:
                while self.source_code[self.current_source_index] != start_char:
                    if self.source_code[self.current_source_index] in ["\0", "\n"]:
                        error("Unterminated string!", self.line_num)
                    string_constant += self.source_code[self.current_source_index]
                    self.current_source_index += 1
        elif start_char == '"':
            while self.source_code[self.current_source_index] != start_char:
                if self.source_code[self.current_source_index] == "\0" or self.source_code[self.current_source_index] == "\n":
                    error("Unterminated string!", self.line_num)
                string_constant += self.source_code[self.current_source_index]
                if (
                    self.source_code[self.current_source_index] == "\\"
                    and self.source_code[self.current_source_index - 1] != "\\"
                    and self.source_code[self.current_source_index + 1] == '"'
                ):
                    string_constant += self.source_code[self.current_source_index + 1]
                    self.current_source_index += 2
                else:
                    self.current_source_index += 1

        # Skip the " character so that it does not loop back to this function incorrectly
        self.current_source_index += 1

        # Determine the type of data
        type = "char"
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
            type = "string"

        # Put appropriate quote
        string_constant = (
            '"' + string_constant + '"' if type == "string" else "'" + string_constant + "'"
        )

        # Make entry in symbol table
        id = self.table.entry(string_constant, type, "constant")

        # Return string token and current index in source code
        self.tokens.append(Token("string", id, self.line_num))


    def keyword_identifier(self):
        """
        Process keywords and identifiers in source code

        Params
        ======
        self.source_code (string) = The string containing simc source code
        self.current_source_index           (int)    = The current index in the source code
        self.table       (SymbolTable) = Symbol self.table constructed holding information about identifiers and constants
        self.line_num    (int)         = Line number

        Returns
        =======
        Token, int: The token generated for the keyword or identifier and the current position in source code
        """

        value = ""

        # Loop until we get a non-digit character
        while is_alnum(self.source_code[self.current_source_index]):
            value += self.source_code[self.current_source_index]
            self.current_source_index += 1

        #converts boolean const true to integer 1
        if value == "true" or value == "false":
            self.tokens.append(Token("bool",
                        self.table.entry(value, "bool", "constant"),
                        self.line_num))
            return
        
        # Check if value is a math constant or not
        if value in ["PI", "E", "inf", "NaN"]:
            self.tokens.append(Token("number", self.table.entry(value, "double", "constant"), self.line_num))
            return

        # Check if value is keyword or not
        if self.is_keyword(value):
            self.tokens.append(Token(value, "", self.line_num))
            return 

        # Check if identifier is in symbol self.table
        id = self.table.get_by_symbol(value)

        C_keywords = [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double", "else", "enum",
            "extern", "float", "for", "goto", "if", "int", "long", "register", "return", "short", "signed",
            "sizeof", "static", "struct", "switch", "typedef", "union", "unsigned", "void", "volatile", "while"
        ]

        # Check if identifier is a keyword in class
        if value in C_keywords:
            error("A keyword cannot be an identifier - %s" % value, self.line_num)

        # If identifier is not in symbol self.table then give a placeholder datatype var
        if id == -1:
            id = self.table.entry(value, "var", "variable")

        # Return id token and current index in source code
        self.tokens.append(Token("id", id, self.line_num))


    def get_raw_tokens(self):
        """
        makes tokens of each line in C, written between BEGIN_C and END_C

        Params
        ======
        self.source_code (string) = The string containing simc source code
        self.current_source_index           (int)    = The current index in the source code
        self.line_num    (int)         = Line number

        Returns
        =======
        [Token], int,int: List of raw tokens, current place in self.source_code, current line_number in self.source_code
        """

        # keep self.line_num to show in case of error
        begin = self.line_num
        tokens = []
        while True:
            val = ""

            # capture whole line
            while self.source_code[self.current_source_index] != "\n" and self.source_code[self.current_source_index] != "\0":
                val += self.source_code[self.current_source_index]
                self.current_source_index += 1

            # if END_C found, add 1 to account for newline, and return
            if val.strip() == "END_C":
                self.current_source_index += 1
                self.line_num += 1
                return

            elif self.source_code[self.current_source_index] == "\0":
                error("No matching END_C found to BEGIN_C", begin)
            else:
                self.tokens.append(Token("RAW_C", val, self.line_num))

            # increment self.current_source_index and self.line_num to go to next line
            self.current_source_index += 1
            self.line_num += 1


    def lexical_analyze(self):
        """
        Generate tokens from source code

        Params
        ======
        filename    (string)      = The string containing simc source code filename
        self.table       (SymbolTable) = Symbol self.table constructed holding information about identifiers and constants

        Returns
        ========
        list: A list of tokens of the source code, if the code is lexically correct, otherwise
            presents user with an error
        """

        self.source_code = self.read_source_code()
        self.current_source_index = 0

        self.initialize_flags_counters()

        self.tokens = []

        while self.source_code[self.current_source_index] != "\0":

            # If we have encountered BEGIN_C, copy everything exactly same until END_C
            if self.raw_c:
                self.get_raw_tokens()
                self.raw_c = False
                self.got_num_or_var = False

            # If a digit appears, call numeric_val function and add the numeric token to list,
            # if it was correct
            if is_digit(self.source_code[self.current_source_index]):
                self.numeric_val()
                self.got_num_or_var = True

            # If double quote appears the value is a string token
            elif self.source_code[self.current_source_index] == '"':
                self.string_val()
                self.got_num_or_var = False

            # If single quote appears the value is a string token
            elif self.source_code[self.current_source_index] == "'":
                self.string_val(start_char="'")
                self.got_num_or_var = False

            # If alphabet or number appears then it might be either a keyword or an identifier
            elif is_alnum(self.source_code[self.current_source_index]):
                self.keyword_identifier()

                if self.tokens[-1].type == "id":
                    self.got_num_or_var = True
                    if self.is_id_module_name:
                        self.is_id_module_name = not self.is_id_module_name

                        module_name, _, _ = self.table.get_by_id(self.tokens[-1].val)
                        module_path = os.path.join(self.module_dir, module_name + ".simc")

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
                    self.raw_c = True
                    continue
                elif self.tokens[-1].type == "END_C":
                    self.raw_c = False
                    continue
                elif self.tokens[-1].type == "import":
                    self.is_id_module_name = True

            # Identifying left paren token
            elif self.source_code[self.current_source_index] == "(":
                # To check if brackets are balanced:
                self.top += 1
                self.balanced_brackets_stack.append("(")

                self.parantheses_count += 1
                self.tokens.append(Token("left_paren", "", self.line_num))
                self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying right paren token
            elif self.source_code[self.current_source_index] == ")":
                # To check if brackets are balanced:
                if self.top == -1:
                    # If at any time there is underflow, there are too many closing brackets.
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
                        self.current_source_index += 1

                    # Add call_end at end of an expression, which is detected as ")" followed by end line or "{"
                    if self.source_code[self.current_source_index + 1] in ["\n", "{", "}", ","]:
                        self.tokens.append(Token("call_end", "", self.line_num))

                else:
                    error("Parentheses does not match", self.line_num)

                self.got_num_or_var = False
                self.current_source_index += 1

            # Identifying end of expression
            elif self.source_code[self.current_source_index] == "\n":
                if self.parantheses_count == 0:
                    self.tokens.append(Token("newline", "", self.line_num))
                else:
                    error("Parentheses does not match.", self.line_num)

                self.current_source_index += 1
                self.line_num += 1

            # Identifying left brace token
            elif self.source_code[self.current_source_index] == "{":
                # To check if brackets are balanced:
                self.top += 1
                self.balanced_brackets_stack.append("{")

                self.tokens.append(Token("left_brace", "", self.line_num))
                self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying right brace token
            elif self.source_code[self.current_source_index] == "}":
                # To check if brackets are balanced:
                if self.top == -1:
                    # If at any time there is underflow, there are too many closing brackets.
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]
                    error("Too many closing braces", self.line_num)
                elif self.balanced_brackets_stack[self.top] != "{":
                    error("Unbalanced braces error", self.line_num)

                else:
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]

                self.tokens.append(Token("right_brace", "", self.line_num))
                self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying left bracket token
            elif self.source_code[self.current_source_index] == "[":
                # To check if brackets are balanced:
                self.top += 1
                self.balanced_brackets_stack.append("[")

                self.tokens.append(Token("left_bracket", "", self.line_num))
                self.current_source_index += 1

            # Identifying right bracket token
            elif self.source_code[self.current_source_index] == "]":
                # To check if brackets are balanced:
                if self.top == -1:
                    # If at any time there is underflow, there are too many closing brackets.
                    self.top -= 1
                    self.balanced_brackets_stack = self.balanced_brackets_stack[:-1]
                    error("Too many closing brackets", self.line_num)
                elif balanced_brackets_stack[top] != "[":
                    error("Unbalanced brackets error", self.line_num)

                else:
                    self.top -= 1
                    balanced_brackets_stack = balanced_brackets_stack[:-1]

                self.tokens.append(Token("right_bracket", "", self.line_num))
                self.current_source_index += 1

            # Identifying assignment token or equivalence token
            elif self.source_code[self.current_source_index] == "=":
                if self.source_code[self.current_source_index + 1] != "=":
                    self.tokens.append(Token("assignment", "", self.line_num))
                    self.current_source_index += 1
                else:
                    self.tokens.append(Token("equal", "", self.line_num))
                    self.current_source_index += 2
                self.got_num_or_var = False

            # Identifying plus_equal, increment or plus token
            elif self.source_code[self.current_source_index] == "+":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("plus_equal", "", self.line_num))
                    self.current_source_index += 2
                elif self.source_code[self.current_source_index + 1] == "+":
                    self.tokens.append(Token("increment", "", self.line_num))
                    self.current_source_index += 2
                else:
                    self.tokens.append(Token("plus", "", self.line_num))
                    self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying minus_equal, decrement or minus token
            elif self.source_code[self.current_source_index] == "-":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("minus_equal", "", self.line_num))
                    self.current_source_index += 2
                elif self.source_code[self.current_source_index + 1] == "-":
                    self.tokens.append(Token("decrement", "", self.line_num))
                    self.current_source_index += 2
                else:
                    self.tokens.append(Token("minus", "", self.line_num))
                    self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying multiply_equal or multiply token
            elif self.source_code[self.current_source_index] == "*":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("multiply_equal", "", self.line_num))
                    self.current_source_index += 2
                # introducing new symbol for power -> pow(a,b) in c
                # is a**b in simc instead of a^b
                elif self.source_code[self.current_source_index + 1] == "*":
                    self.tokens.append(Token("power", "", self.line_num))
                    self.current_source_index += 2
                else:
                    self.tokens.append(Token("multiply", "", self.line_num))
                    self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying xor token
            elif self.source_code[self.current_source_index] == "^":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("bitwise_xor_equal", "", self.line_num))
                    self.current_source_index += 1
                else:
                    self.tokens.append(Token("bitwise_xor", "", self.line_num))
                self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying 'address of','and', 'bitwise and' token
            elif self.source_code[self.current_source_index] == "&":
                if self.source_code[self.current_source_index + 1] == "&":
                    self.tokens.append(Token("and", "", self.line_num))
                    self.current_source_index += 2
                else:
                    if self.got_num_or_var:
                        if self.source_code[self.current_source_index + 1] == "=":
                            self.tokens.append(Token("bitwise_and_equal", "", self.line_num))
                            self.current_source_index += 1
                        else:
                            self.tokens.append(Token("bitwise_and", "", self.line_num))
                        self.current_source_index += 1
                    else:
                        self.tokens.append(Token("address_of", "", self.line_num))
                        self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying 'or' token
            elif self.source_code[self.current_source_index] == "|":
                if self.source_code[self.current_source_index + 1] == "|":
                    self.tokens.append(Token("or", "", self.line_num))
                    self.current_source_index += 2
                elif self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("bitwise_or_equal", "", self.line_num))
                    self.current_source_index += 2
                else:
                    self.tokens.append(Token("bitwise_or", "", self.line_num))
                    self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying divide_equal or divide token
            elif self.source_code[self.current_source_index] == "/":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("divide_equal", "", self.line_num))
                    self.current_source_index += 2
                # to check if it is a single line comment
                elif self.source_code[self.current_source_index + 1] == "/":
                    self.current_source_index += 2
                    while self.source_code[self.current_source_index] != "\n":
                        self.comment_str += str(self.source_code[self.current_source_index])
                        self.current_source_index += 1
                    self.tokens.append(Token("single_line_comment", self.comment_str, self.line_num))
                    self.comment_str = ""
                # to check if it is a multi line comment
                elif self.source_code[self.current_source_index + 1] == "*":
                    self.current_source_index += 2
                    while self.source_code[self.current_source_index : self.current_source_index + 2] != "*/":
                        if self.source_code[self.current_source_index] == "\n":
                            self.line_num += 1
                        self.comment_str += str(self.source_code[self.current_source_index])
                        self.current_source_index += 1
                    self.current_source_index += 2
                    self.tokens.append(Token("multi_line_comment", self.comment_str, self.line_num))
                    self.comment_str = ""
                else:
                    self.tokens.append(Token("divide", "", self.line_num))
                    self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying modulus_equal or modulus token
            elif self.source_code[self.current_source_index] == "%":
                if self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("modulus_equal", "", self.line_num))
                    self.current_source_index += 2
                else:
                    self.tokens.append(Token("modulus", "", self.line_num))
                    self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying comma token
            elif self.source_code[self.current_source_index] == ",":
                self.tokens.append(Token("comma", "", self.line_num))
                self.current_source_index += 1
                self.got_num_or_var = False

            # Identifying not_equal token
            elif self.source_code[self.current_source_index] == "!" and self.source_code[self.current_source_index + 1] == "=":
                self.tokens.append(Token("not_equal", "", self.line_num))
                self.current_source_index += 2
                self.got_num_or_var = False

            # Identifying greater_than or greater_than_equal token
            elif self.source_code[self.current_source_index] == ">":
                if self.source_code[self.current_source_index + 1] not in ["=", ">"]:
                    self.tokens.append(Token("greater_than", "", self.line_num))
                    self.current_source_index += 1
                elif self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("greater_than_equal", "", self.line_num))
                    self.current_source_index += 2
                else:
                    self.tokens.append(Token("right_shift", "", self.line_num))
                    self.current_source_index += 2
                self.got_num_or_var = False

            # Identifying less_than or less_than_equal token
            elif self.source_code[self.current_source_index] == "<":
                if self.source_code[self.current_source_index + 1] not in ["<", "="]:
                    self.tokens.append(Token("less_than", "", self.line_num))
                    self.current_source_index += 1
                elif self.source_code[self.current_source_index + 1] == "=":
                    self.tokens.append(Token("less_than_equal", "", self.line_num))
                    self.current_source_index += 2
                elif self.source_code[self.current_source_index + 1] == "<":
                    self.tokens.append(Token("left_shift", "", self.line_num))
                    self.current_source_index += 2
                self.got_num_or_var = False

            # Identifiying colon token
            elif self.source_code[self.current_source_index] == ":":
                self.tokens.append(Token("colon", "", self.line_num))
                self.current_source_index += 1
                self.got_num_or_var = False

            # Otherwise increment the index
            else:
                self.current_source_index += 1

        # By the end, if stack is not empty, there are extra opening brackets
        if self.top != -1:
            error("Unbalanced parenthesis error", self.line_num)

        # Return the generated tokens
        return self.tokens, self.module_source_paths
