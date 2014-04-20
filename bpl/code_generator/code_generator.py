"""
AUTHOR: Oren Shoham
DATE: 4/9/2014
"""

from bpl.parser.parsetree import *

SP = '%rsp'
FP = '%rbx'
ACC_64 = '%rax'
ACC_32 = '%eax'
ARG2_64 = '%rsi'
ARG2_32 = '%esi'
ARG1_64 = '%rdi'
ARG1_32 = '%edi'

def generate_code(type_checked_parse_tree, output_file):
    compute_offsets(type_checked_parse_tree)
    gen_header(type_checked_parse_tree, output_file)

    declaration = type_checked_parse_tree
    while declaration is not None:
        if declaration.kind == NodeType.FUN_DEC:
            gen_code_function(declaration, output_file)
        declaration = declaration.next_node

def compute_offsets(parse_tree):
    declaration = parse_tree 
    while declaration is not None:
        if declaration.kind == NodeType.FUN_DEC:
            parameter_offset = 0
            param = declaration.params
            while param is not None:
                parameter_offset += 8
                param.offset = parameter_offset
                param = param.next_node
            declaration.local_var_offset = compute_offsets_statement(declaration.body, 0)
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

        total = offset
        stmnt = statement.statements
        while stmnt is not None:
            total += compute_offsets_statement(stmnt, offset)
            stmnt = stmnt.next_node
        return total
    
    elif statement.kind == NodeType.IF_STATEMENT:
        total = offset
        total += compute_offsets_statement(statement.statement, offset)
        if statement.else_statement is not None:
            total += compute_offsets_statement(statement.else_statement, offset)
        return total

    elif statement.kind == NodeType.WHILE_STATEMENT:
        total = offset
        total += compute_offsets_statement(statement.statement, offset)
        return total
    
    else: # return a total local variable offset of 0
        return 0

def gen_reg_reg(opcode, reg1, reg2, comment, output_file):
    output_file.write('\t{} {}, {} #{}\n'.format(opcode, reg1, reg2, comment))

def gen_immediate_reg(opcode, immediate, reg, comment, output_file):
    output_file.write('\t{} ${}, {} #{}\n'.format(opcode, immediate, reg, comment))

def gen_no_operands(opcode, comment, output_file):
    output_file.write('\t{} #{}\n'.format(opcode, comment))

def gen_one_operand(opcode, operand, comment, output_file):
    output_file.write('\t{} {} #{}\n'.format(opcode, operand, comment))

def gen_header(parse_tree, output_file):
    output_file.write('.section .rodata\n')
    output_file.write('.WriteIntString: .string "%d "\n')
    output_file.write('.WritelnString: .string "\\n"\n')
    output_file.write('.WriteStringString: .string "%s "\n')
    output_file.write('.ArrayOverflowString: .string "You fell off the end of an array.\\n"\n')
    output_file.write('.ReadIntString: .string "%d"\n')
    output_file.write('.text\n')
    output_file.write('.globl main\n')

def gen_code_function(function, output_file):
    output_file.write(function.name + ':\n')
    gen_reg_reg('movq', SP, FP, 'set up the frame pointer', output_file)
    gen_immediate_reg('sub', function.local_var_offset, SP, 'allocate local variables', output_file)
    # generate function body code
    gen_immediate_reg('add', function.local_var_offset, SP, 'deallocate local variables', output_file)
    gen_no_operands('ret', 'return from function "{}"'.format(function.name), output_file)

def gen_code_statement(statement, output_file):
    if statement.kind == NodeType.WRITE_STATEMENT:
        if statement.expression.kind == NodeType.NUM_EXP:
            gen_immediate_reg('movl', statement.expression.number, ACC_32, 'put write statement integer value into accumulator', output_file)
            gen_reg_reg('movl', ACC_32, ARG1_32, 'integer value to print = arg2', output_file)
            gen_immediate_reg('movq', '.WriteIntString', ARG1_64, 'printf integer formatting string = arg1', output_file)
            gen_immediate_reg('movl', 0, ACC_32, 'clear the return value', output_file)
            gen_one_operand('call', 'printf', 'call the C-lib printf function', output_file)
        else: # statement.expression.kind == NodeType.STR_EXP
            gen_immediate_reg('movq', statement.expression.string, ACC_64, 'put write statement string value into accumulator', output_file)
