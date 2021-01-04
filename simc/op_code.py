class OpCode:
    """
    OpCode class is responsible for creating opcodes
    """

    def __init__(self, opcode, val, dtype=None):
        """
        Initializer of OpCode class

        Params
        ======
        opcode           (string) = Type of opcode as string
        val              (string) = Value stored at opcode
        dtype (Optional) (string) = Datatype of opcode
        """

        self.type = opcode
        self.val = val
        self.dtype = dtype

    def __str__(self):
        """
        Returns string representation of OpCode

        Returns
        =======
        string: The string representation of OpCode object, which can be used to print the opcodes
        """

        return "OpCode('%s', '%s', '%s')" % (self.type, self.val, self.dtype)

    def __eq__(self, other):
        """
        Check for equality of opcodes

        Returns
        =======
        bool: Whether a token object is equal to another or not
        """

        if (
            self.type == other.type
            and self.val == other.val
            and self.dtype == other.dtype
        ):
            return True

        return False
