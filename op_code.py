class OpCode():
    """
        OpCode class is responsible for creating opcodes
    """

    def __init__(self, opcode, val):
        """
            Params
            ======
            type     (string) = type of opcode as string
            val      (string) = value stored at opcode

            Values
            ======
            type     (string) = type of opcode as string
            typedig  (int)    = type of opcode as integer
            val      (string) = value stored at opcode
        """

        self.type = opcode
        self.typedig = self.opcode2dig(type)
        self.val = val

    def __str__(self):
        """
            Returns
            =======
            The string representation of OpCode object, which can be used to print the opcodes
        """

        return "OpCode(%s, %s)" % (self.opcode, self.val)

    def opcode2dig(self, str_type):
        """
            Params
            ======
            str_type (string) = String representation of opcode type

            Returns
            =======
            The integer representation of the string opcode
        """

        dic = {"print": 1}
        return dic.get(str_type, 0)
