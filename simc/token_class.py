class Token:
    """
    Token class is responsible for creating tokens
    """

    def __init__(self, type, val, line_num, scope):
        """
        Class initializer

        Params
        ======
        type     (string) = Type of token as string
        val      (string) = Value stored at token
        line_num (int)    = Line number
        scope    (string) = Scope of token
        """

        self.type = type
        self.val = val
        self.line_num = line_num
        self.scope = scope

    def __str__(self):
        """
        String representation of a Token

        Returns
        =======
        string: The string representation of Token object, which can be used to print the tokens
        """

        return "Token('%s', '%s', '%s', '%s')" % (self.type, self.val, self.line_num, self.scope)

    def __eq__(self, other):
        """
        Check for equality of tokens

        Returns
        =======
        bool: Whether a token object is equal to another or not
        """

        if (
            self.type == other.type
            and self.val == other.val
            and self.line_num == other.line_num
            and self.scope == other.scope
        ):
            return True

        return False
