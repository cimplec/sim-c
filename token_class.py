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
            The string representation of Token object, which can be used to print the tokens
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

        dic = {"number": 1, "string": 2, "print": 3, "identifier": 4, "left_paren": 5, "right_paren": 6}
        return dic.get(str_type, 0)
