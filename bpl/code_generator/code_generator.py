"""
AUTHOR: Oren Shoham
DATE: 4/9/2014
"""

from bpl.parser.parsetree import *
from bpl.scanner.token import TokenType

# Register names
SP = 'rsp'
FP = 'rbx'
ACC_64 = 'rax'
ACC_32 = 'eax'
ARG1_64 = 'rdi'
ARG1_32 = 'edi'
ARG2_64 = 'rsi'
ARG2_32 = 'esi'
ARG3_64 = 'rdx'
ARG3_32 = 'edx'
ARG4_64 = 'rcx'
ARG4_32 = 'ecx'
ARG5_64 = 'r8'
ARG5_32 = 'r8d'
ARG6_64 = 'r9'
ARG6_32 = 'r9d'
CALLEE_SAVED_1_64 = 'rbx'
CALLEE_SAVED_1_32 = 'ebx'
CALLEE_SAVED_2_64 = 'rbp'
CALLEE_SAVED_2_32 = 'ebp'
CALLEE_SAVED_3_64 = 'r10'
CALLEE_SAVED_3_32 = 'r10d'
CALLEE_SAVED_4_64 = 'r13'
CALLEE_SAVED_4_32 = 'r13d'
CALLEE_SAVED_5_64 = 'r14'
CALLEE_SAVED_5_32 = 'r14d'
CALLEE_SAVED_6_64 = 'r15'
CALLEE_SAVED_6_32 = 'r15d'

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
    output_file.write('\t{} %{}, %{} #{}\n'.format(opcode, reg1, reg2, comment))

def gen_immediate_reg(opcode, immediate, reg, comment, output_file):
    output_file.write('\t{} ${}, %{} #{}\n'.format(opcode, immediate, reg, comment))

def gen_indirect_reg(opcode, offset, reg1, reg2, comment, output_file):
    output_file.write('\t{} {}(%{}), %{} #{}\n'.format(opcode, offset, reg1, reg2, comment))

def gen_reg_indirect(opcode, reg1, offset, reg2, comment, output_file):
    output_file.write('\t{} %{}, {}(%{}) #{}\n'.format(opcode, reg1, offset, reg2, comment))

def gen_no_operands(opcode, comment, output_file):
    output_file.write('\t{} #{}\n'.format(opcode, comment))

def gen_direct(opcode, operand, comment, output_file):
    output_file.write('\t{} {} #{}\n'.format(opcode, operand, comment))

def gen_reg(opcode, reg, comment, output_file):
    output_file.write('\t{} %{} #{}\n'.format(opcode, reg, comment))

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
    gen_code_statement(function.body, output_file)
    gen_immediate_reg('add', function.local_var_offset, SP, 'deallocate local variables', output_file)
    gen_no_operands('ret', 'return from function "{}"'.format(function.name), output_file)

def gen_code_statement(statement, output_file):
    if statement.kind == NodeType.CMPND_STATEMENT:
        # do some other stuff
        stmnt = statement.statements
        while stmnt is not None:
            gen_code_statement(stmnt, output_file)
            stmnt = stmnt.next_node
        
    if statement.kind == NodeType.WRITE_STATEMENT:
        gen_code_expression(statement.expression, output_file)
        if statement.expression.kind in (NodeType.NUM_EXP, NodeType.MATH_EXP):
            gen_reg_reg('movl', ACC_32, ARG2_32, 'integer value to print = arg2', output_file)
            gen_immediate_reg('movq', '.WriteIntString', ARG1_64, 'printf integer formatting string = arg1', output_file)
            gen_immediate_reg('movl', 0, ACC_32, 'clear the return value', output_file)
            gen_direct('call', 'printf', 'call the C-lib printf function', output_file)
        elif statement.expression.kind == NodeType.STR_EXP:
            pass

def gen_code_expression(expression, output_file):
    if expression.kind == NodeType.NUM_EXP:
        gen_immediate_reg('movl', expression.number, ACC_32, 'put an integer value into the accumulator', output_file)

    elif expression.kind == NodeType.STR_EXP: 
        gen_immediate_reg('movq', expression.string, ACC_64, 'put a string value into the accumulator', output_file)

    elif expression.kind == NodeType.MATH_EXP:
        gen_code_expression(expression.left, output_file)
        gen_reg('push', ACC_64, 'push the value of the left side of arithmetic expression onto the stack', output_file)
        gen_code_expression(expression.right, output_file)

        if expression.token.kind == TokenType.T_PLUS:
            gen_indirect_reg('addl', 0, SP, ACC_32, 'add the left side of the arithmetic expression to the right side', output_file)

        elif expression.token.kind == TokenType.T_MINUS:
            gen_reg_indirect('sub', ACC_32, 0, SP, 'subtract the right side of the arithmetic expression from the left side', output_file)
            gen_indirect_reg('movl', 0, SP, ACC_32, 'put the result of the subtraction into the accumulator', output_file)

        elif expression.token.kind == TokenType.T_MULT:
            gen_indirect_reg('imul', 0, SP, ACC_32, 'multiply the left side of the arithmetic expression by the right side', output_file)

        elif expression.token.kind in (TokenType.T_DIV, TokenType.T_MOD):
            gen_reg('push', CALLEE_SAVED_2_64, 'save the value in the %ebp register on the stack', output_file)
            gen_reg_reg('movl', ACC_32, CALLEE_SAVED_2_32, 'put the divisor into the %ebp register', output_file)
            gen_indirect_reg('movl', 8, SP, ACC_32, 'put the dividend into the accumulator', output_file)
            gen_no_operands('cltq', 'sign-extend dividend to rax', output_file)
            gen_no_operands('cqto', 'sign_extend dividend to rdx', output_file)
            gen_reg('idivl', CALLEE_SAVED_2_32, 'perform the division operation', output_file)

            if expression.token.kind == TokenType.T_MOD:
                # place the remainder into the accumulator instead of the quotient
                gen_reg_reg('movl', ARG3_32, ACC_32, 'put the remainder into the accumulator', output_file)

            gen_reg('pop', CALLEE_SAVED_2_64, 'restore %ebp\'s original value', output_file)

        gen_immediate_reg('addq', 8, SP, 'pop the left side of the arithmetic expression off of the stack', output_file)
