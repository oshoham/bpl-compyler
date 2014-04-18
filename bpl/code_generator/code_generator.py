"""
AUTHOR: Oren Shoham
DATE: 4/9/2014
"""

from bpl.parser.parsetree import *

def generate_code(type_checked_parse_tree, output_file):
    compute_offsets(type_checked_parse_tree)

def compute_offsets(parse_tree):
    declaration = parse_tree 
    while declaration is not None:
        if declaration.kind == NodeType.FUN_DEC:
            parameter_offset = 0
            local_var_offset = 0
            param = declaration.params
            while param is not None:
                parameter_offset += 8
                param.offset = parameter_offset
                param = param.next_node
            compute_offsets_statement(declaration.body, local_var_offset)
        declaration = declaration.next_node

def compute_offsets_statement(statement, offset):
    if statement.kind == NodeType.CMPND_STATEMENT:
        dec = statement.local_declarations
        while dec is not None:
            if dec.kind == NodeType.ARRAY_DEC:
                offset -= 8 * dec.size
            else: # dec.kind == NodeType.VAR_DEC
                offset -= 8
            dec.offset = offset
            dec = dec.next_node

        stmnt = statement.statements
        while stmnt is not None:
            compute_offsets_statement(stmnt, offset)
            stmnt = stmnt.next_node
    
    elif statement.kind == NodeType.IF_STATEMENT:
        compute_offsets_statement(statement.statement, offset)
        if statement.else_statement is not None:
            compute_offsets_statement(statement.else_statement, offset)

    elif statement.kind == NodeType.WHILE_STATEMENT:
        compute_offsets_statement(statement.statement, offset)

def gen_reg_reg(opcode, reg1, reg2, comment, output_file):
    output_file.write('{} {}, {} #{}\n'.format(opcode, reg1, reg2, comment))
