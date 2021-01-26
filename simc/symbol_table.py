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
    
    def __str__( self ):

        table_dict = self.symbol_table

        # Maximum length when all strings in the lists are compared
        max_length = max( [ len(i)  for dict_list in table_dict.values()  for i in dict_list ] )

        table_string = ""

        # To solve spacing issue for when lines exceed some power of 10 (like from line 9 to 10, 99 to 100 etc. )
        spaces_after_integer = len(str(len(table_dict)))

        for i in range( 1, len( table_dict )+1 ):
            
            line = "| " + str(i) + "  "

            # Without this line, as the number of elements in symbol table exceeds some power of 10,
            # there will be some distortion in table rows. For example, between row 99 and 100.
            line += " " * ( spaces_after_integer - len(str(i)) )

            dict_list = table_dict[ i ]

            for j in range( len(dict_list) ):
                
                line += dict_list[ j ]
                if j < len( dict_list ) - 2:
                    
                    line += " " * (max_length - len(dict_list[j]) + 2 )

            len_horizontal_bar = len( line )
            table_string += line + " |\n"

        horizontal_bar = "|" + "-" * ( len_horizontal_bar ) + "|\n"
        table_string = horizontal_bar + table_string + horizontal_bar
        
        return table_string 

    def entry(self, value, type, typedata, dependency=''):
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

        self.symbol_table[self.id] = [value, type, typedata, dependency]
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

        return self.symbol_table.get(id, [None, None, None, None])

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

    def add_dependency(self, var_father_id, var_child_id):
        """
        Add dependency adds a relation of dependecy beetween two variables.
        It's used when the variable is assigned to other varible before it is type had been defined. 
        When the type of the varible is discovered, use the function resolve_dependency to update the child variables.
        ======
        Params
        ======
        table           (SymbolTable) = Symbol table constructed holding information about identifiers and constants
        var_father_id   (int)         = ID of varible father in SymbolTable
        var_father_id   (int)         = ID of varibl child in SymbolTable
    
        """
        # Add the variable to list in the expression:: "<-ID>"
        self.symbol_table[var_father_id][3] += '-' + str(var_child_id)


    def resolve_dependency(self, tokens, i, var_id):
        """
        Resolve Dependency

        This is a recursive function, it is used when you discover the type of a varible which had been 
        assign to another one, then the type of the assigned one dependes on this.
        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
        var_id      (int)  = ID in Symbol table where the function will look at for child dependencies
        """
        # Extract the type of variable and the list of variable which dependies on it
        _, type_, _, list_dependency = self.symbol_table[var_id]
        
        # Nothing to do
        if type_ == "var":
            return

        # Clear the dependencies
        self.symbol_table[var_id][3] = ''

        # Split the list "ID-ID-...-ID" => ['ID', 'ID', ..., 'ID']
        list_dependency = [int(child_var_id) for child_var_id in \
                            list_dependency.split('-') if child_var_id != '']

        is_allowed = True 

        # For each child variable assign the new type and check up for its dependencies. 
        for var_child_id in list_dependency: 

            if is_allowed is False:
                break

            # Extract the current type of child variable
            child_type = self.symbol_table[var_child_id][1]

            # If the type is not defined
            if child_type == "declared":
                if type_ == "string":
                    type_ = "char*"
                self.symbol_table[var_child_id][1] = type_
                is_allowed = self.resolve_dependency(tokens, i, var_child_id)

           # If the type is defined, it cannot downgrade 
            elif child_type > type_:
                self.symbol_table[var_child_id][1] = type_
            
             # if the type is defined and the type of child is greater or equal than the father
            elif child_type < type_:
                is_allowed = False
        
        return is_allowed