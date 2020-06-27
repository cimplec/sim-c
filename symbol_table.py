class SymbolTable():

    def __init__(self):
        self.id = 1
        self.symbol_table = {}

    def entry(self, value, type, typedata):
        self.symbol_table[self.id] = [value, type, typedata]
        self.id += 1
        return self.id - 1

    def get_by_id(self, id):
        return self.symbol_table[id]

    def get_by_symbol(self, value):
        id = -1
        for ids, value_list in self.symbol_table.items():
            if value_list[0] == value:
                return ids
        return id
