from ..global_helpers import error, check_if

from ..op_code import OpCode


def initializate_struct(tokens, i, table, instance_var_name, var_list):
    """
        Initialization of a struction when the variable instantiate is type of a declared struct
        Params
        ======
        tokens      (list) = List of tokens
        i           (int)  = Current index in token
        table               (SymbolTable) = Symbol Table constructed holding information about identifiers and constans
        instance_var_name   (String)      = Name of the instance of the struct
        var_list            (String)      = List of if variable declared inside struct
    """    
    # Initializate the child variable of struct
    var_ids = var_list.split('-')[1:]
    
    # Load var and copy to struct initilization 
    for var_id in var_ids:

        # Find the child variable of struct 
        var_name, type_, metatype_, _ = table.get_by_id(int(var_id))
        new_var_name = instance_var_name + "." + var_name

        # Check if variable already exist
        new_var_id = table.get_by_symbol(new_var_name)
        # If it not exist, then create a new
        if new_var_id is -1:
            table.entry(instance_var_name + "." + var_name, type_, metatype_, '')
        # Otherwise, Modify datatype of the identifier
        else:
            table.symbol_table[new_var_id][1] = type_
            table.symbol_table[new_var_id][3] += '-' + var_id

def struct_declaration_statement(tokens, i, table):
    """
    Parse structure declaration statement
    Params
    ======
    tokens      (list) = List of tokens
    i           (int)  = Current index in token
    table       (SymbolTable) = Symbol table constructed holding information about identifiers and constants
    Returns
    =======
    OpCode, int, string: The opcode for the assign code, the index, and the name of the function after
                         parsing function calling statement
    """

    from .simc_parser import skip_all_nextlines

    # Check if identifier follows struct
    check_if(got_type=tokens[i].type, should_be_types="id", 
             error_msg="Expected structure name", line_num=tokens[i].line_num)

    # Store the id of strcuture name in symbol table
    struct_idx = tokens[i].val

    # Update type to hold struct_var instead of var 
    table.symbol_table[struct_idx][1] = "struct_var"

    # Get struct name
    struct_name, _, _, _ = table.get_by_id(struct_idx)

    # If \n follows struct name then skip all the \n characters
    if tokens[i + 1].type == "newline":
        i = skip_all_nextlines()
        i -= 1

    # Check if { follows the structure name
    check_if(
        got_type=tokens[i + 1].type,
        should_be_types="left_brace",
        error_msg="Expected { after structure name body",
        line_num=tokens[i + 1].line_num,
    )

    # Loop until } is reached
    i += 2
    ret_idx = i
    found_right_brace = False
    while i < len(tokens) and tokens[i].type != "right_brace":
        i += 1

    # If right brace found at end
    if i != len(tokens) and tokens[i].type == "right_brace":
        found_right_brace = True

    # If right brace is not found then produce error
    if not found_right_brace:
        error("Expected } after structure body", tokens[i].line_num)

    return (OpCode("struct_decl", struct_name, ""), ret_idx - 1, struct_name)