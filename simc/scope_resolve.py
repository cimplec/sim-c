from .token_class import Token


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
        id_usage_to_resolve = []
        function_started = False

        for i, token in enumerate(self.__tokens_list):
            if i > 0 and self.__tokens_list[i-1].type == "fun" and token.type == "id":
                self.__push_to_scope_stack(Token("left_brace", "", token.line_num))
                function_started = True
            elif i > 0 and self.__tokens_list[i-1].type == "var" and token.type == "id":
                self.__push_to_scope_stack(token)
            elif token.type == "id" and function_started:
                self.__push_to_scope_stack(token)
            elif token.type == "call_end" and function_started:
                function_started = False
            elif token.type == "id":
                id_usage_to_resolve.append(i)
            elif i > 0 and token.type == "left_brace" and self.__tokens_list[i-1].type != "call_end":
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
                self.__symbol_table.symbol_table[top_token_id][-1] += "-" + str(final_line)

        for id_ in id_usage_to_resolve:
            resolved_id = self.__symbol_table.resolve_scope_for_id(token=self.__tokens_list[id_])
            self.__tokens_list[id_].val = resolved_id if resolved_id != None else self.__tokens_list[id_].val
            

        return self.__tokens_list, self.__symbol_table