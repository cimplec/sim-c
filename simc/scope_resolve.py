class ScopeResolver:

    def __init__(self, tokens_list, symbol_table):
        self.__tokens_list = tokens_list
        self.__symbol_table = symbol_table
        self.__scope_stack = []

    def __push_to_scope_stack(self, val):
        self.__scope_stack.append(val)

    def __pop_from_scope_stack(self):
        return self.__scope_stack.pop()

    def resolve_scope(self):
        final_line = 0

        for i, token in enumerate(self.__tokens_list):
            if i > 0 and self.__tokens_list[i-1].type == "var" and token.type == "id":
                self.__push_to_scope_stack(token)
            elif token.type == "left_brace":
                self.__push_to_scope_stack(token)
            elif token.type == "right_brace":
                while len(self.__scope_stack) != 0:
                    top_token = self.__pop_from_scope_stack()
                    
                    if top_token.type == "id":
                        top_token_id = top_token.val
                        self.__symbol_table.symbol_table[top_token_id][-1] += "-" + str(token.line_num)
                    elif top_token.type == "left_brace":
                        break

            final_line = token.line_num

 
        while len(self.__scope_stack) != 0:
            top_token = self.__pop_from_scope_stack()

            if top_token.type == "id":
                top_token_id = top_token.val
                self.__symbol_table.symbol_table[top_token_id][-1] += "-" + str(token.line_num)

        return self.__symbol_table