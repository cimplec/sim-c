class OpCode():
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

            Values
            ======
            type     (string) = Type of opcode as string
            typedig  (int)    = Type of opcode as integer
            val      (string) = Value stored at opcode
            dtype    (string) = Datatype of opcode
        """

        self.type = opcode
        self.typedig = self.opcode2dig(type)
        self.val = val
        self.dtype = dtype

    def __str__(self):
        """
            Returns string representation of the object of this class

            Returns
            =======
            string: The string representation of OpCode object, which can be used to print the opcodes
        """

        return "OpCode(%s, %s, %s)" % (self.type, self.val, self.dtype)

    def opcode2dig(self, str_type):
        """
            Returns integer representation of opcode type

            Params
            ======
            str_type (string) = String representation of opcode type

            Returns
            =======
            int: The integer representation of the string opcode
        """

        dic = {"print": 1, "var_assign": 2, "var_no_assign": 3, "assign": 4, "func_decl": 5, "while": 6}
        return dic.get(str_type, 0)
