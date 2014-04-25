"""
AUTHOR: Oren Shoham
DATE: 4/9/2014
"""

from bpl.parser.parsetree import *
from bpl.scanner.token import TokenType
from itertools import count

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

# infinite label generator
labels = count()
next_label = lambda : '.L{}'.format(next(labels))

string_table = {}

def generate_code(type_checked_parse_tree, output_file):
    """Top-level code generation function."""
    compute_offsets(type_checked_parse_tree)
    gen_header(type_checked_parse_tree, output_file)

    declaration = type_checked_parse_tree
    while declaration is not None:
        if declaration.kind == NodeType.FUN_DEC:
            gen_code_function(declaration, output_file)
        declaration = declaration.next_node

def compute_offsets(parse_tree):
    """Walks through the top-level declarations in parse_tree, computing stack pointer offsets for function parameters and local variables."""
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
    """Computes stack pointer offsets for local variable declarations and updates parse tree statement node fields appropriately."""
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

    elif statement.kind == NodeType.IF_STATEMENT:
        continue_label = next_label()
        gen_code_expression(statement.condition, output_file)
        gen_immediate_reg('cmpl', 0, ACC_32, 'check whether the if condition evaluates to true or false', output_file)
        if statement.else_statement is not None:
            else_label = next_label()
            # generate jump to else if false code
            gen_direct('je', else_label, 'jump to else statement code if condition evaluates to false', output_file)
            gen_code_statement(statement.statement, output_file)
            gen_direct('jmp', continue_label, 'jump to the end of the if statement code', output_file)
            output_file.write('{}:\n'.format(else_label))
            gen_code_statement(statement.else_statement, output_file)
        else:
            # generate jump if true code
            gen_direct('je', continue_label, 'jump over if statement code if condition evaluates to false', output_file)
            gen_code_statement(statement.statement, output_file)
        output_file.write('{}:\n'.format(continue_label))

    # generate code for return statements
    elif statement.kind == NodeType.RETURN_STATEMENT:
        # move the return value into the accumulator
        gen_code_expression(statement.expression, output_file)
        gen_no_operands('ret', 'return from the current function', output_file)

def gen_code_expression(expression, output_file):
    if expression.kind == NodeType.NUM_EXP:
        gen_immediate_reg('movl', expression.number, ACC_32, 'put an integer value into the accumulator', output_file)

    elif expression.kind == NodeType.STR_EXP: 
        #gen_immediate_reg('movq', expression.string, ACC_64, 'put a string value into the accumulator', output_file)
        pass

    # generate code for arithmetic expressions
    elif expression.kind == NodeType.MATH_EXP:
        gen_code_expression(expression.left, output_file)
        gen_reg('push', ACC_64, 'push the value of the left side of arithmetic expression onto the stack', output_file)
        gen_code_expression(expression.right, output_file)

        # addition
        if expression.token.kind == TokenType.T_PLUS:
            gen_indirect_reg('addl', 0, SP, ACC_32, 'add the left side of the arithmetic expression to the right side', output_file)

        # subtraction
        elif expression.token.kind == TokenType.T_MINUS:
            gen_reg_indirect('sub', ACC_32, 0, SP, 'subtract the right side of the arithmetic expression from the left side', output_file)
            gen_indirect_reg('movl', 0, SP, ACC_32, 'put the result of the subtraction into the accumulator', output_file)

        # multiplication
        elif expression.token.kind == TokenType.T_MULT:
            gen_indirect_reg('imul', 0, SP, ACC_32, 'multiply the left side of the arithmetic expression by the right side', output_file)

        # division
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

    # generate code for comparison expressions
    elif expression.kind == NodeType.COMP_EXP:
        gen_code_expression(expression.left, output_file)
        gen_reg('push', ACC_64, 'push the value of the left side of the comparison expression onto the stack', output_file)
        gen_code_expression(expression.right, output_file)
        gen_indirect_reg('cmpl', 0, SP, ACC_32, 'compare the two sides of the comparison expression', output_file)

        false_label = next_label()
        true_label = next_label()

        # less than
        if expression.token.kind == TokenType.T_LESS:
            gen_direct('jle', false_label, 'jump to false label if right side of expression is less than or equal to left side'.format(false_label), output_file)

        # less than or equal
        elif expression.token.kind == TokenType.T_LEQ:
            gen_direct('jl', false_label, 'jump to false label if right side of expression is less than left side'.format(false_label), output_file)

        # equal
        elif expression.token.kind == TokenType.T_EQ:
            gen_direct('jne', false_label, 'jump to false label if right side of expression is not equal to left side'.format(false_label), output_file)

        # not equal
        elif expression.token.kind == TokenType.T_NEQ:
            gen_direct('je', false_label, 'jump to false label if right side of expression is equal to left side'.format(false_label), output_file)

        # greater than or equal
        elif expression.token.kind == TokenType.T_GEQ:
            gen_direct('jg', false_label, 'jump to false label if right side of expression is greater than left side'.format(false_label), output_file)

        # greater than
        elif expression.token.kind == TokenType.T_GREATER:
            gen_direct('jge', false_label, 'jump to false label if right side of expression is greater than or equal to left side'.format(false_label), output_file)

        gen_immediate_reg('movl', 1, ACC_32, 'put a non-zero value into the accumulator to indicate that the comparison was true', output_file)
        gen_direct('jmp', true_label, 'skip over code at false label', output_file)
        output_file.write('{}:\n'.format(false_label))
        gen_immediate_reg('movl', 0, ACC_32, 'put zero into the accumulator to indicate that the comparison was false', output_file)
        output_file.write('{}:\n'.format(true_label))
        gen_immediate_reg('addq', 8, SP, 'pop the left side of the comparison expression off of the stack', output_file)

    # generate code for function calls
    elif expression.kind == NodeType.FUN_CALL_EXP:
        args = []
        arg = expression.arguments
        num_args = 0
        while arg is not None:
            args.append(arg)
            arg = arg.next_node
            num_args += 1
        # push the function arguments onto the stack in reverse order
        while len(args) != 0:
            gen_code_expression(args.pop(), output_file)
            gen_reg('push', ACC_64, 'push the function argument onto the stack', output_file)
        gen_reg('push', FP, 'push the frame pointer onto the stack', output_file)
        gen_direct('call', expression.name, 'call function {}'.format(expression.name), output_file)
        gen_reg('pop', FP, 'restore the frame pointer', output_file)
        gen_immediate_reg('addq', num_args*8, SP, 'pop the function arguments off of the stack', output_file)
