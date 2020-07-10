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
            val      (string) = value stored at token

            Values
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
            string: The string representation of Token object, which can be used to print the tokens
        """

        return "Token(%s, %s)" % (self.type, self.val)

    def token2dig(self, str_type):
        """
            Params
            ======
            str_type (string) = String representation of token type

            Returns
            =======
            int: The integer representation of the string token
        """

        dic = {"number": 1, "string": 2, "print": 3, "identifier": 4, "left_paren": 5, "right_paren": 6,
               "var": 7, "assignment": 8, "plus": 9, "minus": 10, "multiply": 11, "divide": 12, "newline": 13,
               "fun": 14, "return": 15, "equal": 16, "not_equal": 17, "greater_than": 18, "less_than": 19, "greater_than_equal": 20, "less_than_equal": 21, "while": 22, "if": 23, "modulus": 24, "increment": 25, "decrement": 26, "plus_equal": 27, "minus_equal": 28, "multiply_equal": 29, "divide_equal": 30, "modulus_equal": 31, "and": 32, "or": 33}

        return dic.get(str_type, 0)
