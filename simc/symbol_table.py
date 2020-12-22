class SymbolTable:
    """
    SymbolTable class is responsible for storing information about identifiers and constants
    """

    def __init__(self):
        """
        Initializer of SymbolTable class
        """

        self.id = 1
        self.symbol_table = {}

    def entry(self, value, type, typedata):
        """
        Returns id in symbol table after making an entry

        Params
        ======
        value    (string) = Value to be stored in symbol table (identifier/constant)
        type     (string) = Datatype of symbol
        typedata (string) = Type of data (constant/variable)

        Returns
        =======
        int: The id of the current entry in symbol table
        """

        self.symbol_table[self.id] = [value, type, typedata]
        self.id += 1
        return self.id - 1

    def get_by_id(self, id):
        """
        Returns symbol table entry by integer unique id

        Params
        ======
        id (id) = Integer unique id of a symbol in the table

        Returns
        =======
        list: [value, type, typedata], typedata = constant/variable
        """

        return self.symbol_table.get(id, [None, None, None])

    def get_by_symbol(self, value):
        """
        Returns unique id of a given value

        Params
        ======
        value (string) = Value to be searched in the symbol table

        Returns
        =======
        int: The unique id of the entry in symbol table
        """

        id = -1
        for ids, value_list in self.symbol_table.items():
            if value_list[0] == value:
                return ids
        return id
