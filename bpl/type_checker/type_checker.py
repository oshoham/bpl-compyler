"""
AUTHOR: Oren Shoham
DATE: long ago in a distant land...
"""

from bpl.parser.parsetree import *
from bpl.scanner.token import TokenType

class TypeCheckerException(Exception):
    def __init__(self, line_number, message):
        message = 'Type Checking Error on line {}: {}'.format(line_number, message)
        Exception.__init__(self, message)

def type_check(parse_tree, debug=False):
    symbol_table = [{}] # this is meant to function as a stack of symbol tables
    find_references(parse_tree, symbol_table, debug)
    # do bottom up pass

def lookup(symbol, symbol_table):
    """Check whether symbol is a key in any of the dictionaries in symbol table, starting at the top of stack.

    Return the parse tree node that is the value of symbol if symbol is a valid key, otherwise None.
    """
    for scope in reversed(range(len(symbol_table))):
        if symbol in symbol_table[scope]:
            return symbol_table[scope][symbol]
    return None

def find_references(parse_tree, symbol_table, debug):
    """Iterate through the top-level declarations of the parse tree and create links between expressions and their declarations."""
    declaration = parse_tree
    while declaration is not None:
        symbol_table[0][declaration.name] = declaration

        if declaration.kind in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
            declaration = declaration.next_node

        elif declaration.kind is NodeType.FUN_DEC:
            local_variables = {}
            param = declaration.params
            while param is not None:
                if param.kind not in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
                    raise TypeCheckerException(param.line_number, 'Function parameter is not a variable, pointer, or array.')
                local_variables[param.name] = param
                param = param.next_node

            symbol_table.append(local_variables) # push local variables onto the symbol table stack
            find_references_statement(declaration.body, symbol_table, debug)
            symbol_table.pop() # pop local variables off of the symbol table stack
            declaration = declaration.next_node

        else:
            raise TypeCheckerException(declaration.line_number, 'Top-level declaration is not a variable, pointer, array, or function.')

def find_references_statement(statement, symbol_table, debug):
    """Create links between expressions associated with a statement and their declarations in the symbol table."""
    if statement.kind is NodeType.EXP_STATEMENT:
        find_references_expression(statement.expression, symbol_table, debug)

    elif statement.kind is NodeType.WHILE_STATEMENT:
        find_references_expression(statement.condition, symbol_table, debug)
        find_references_statement(statement.statement, symbol_table, debug)

    elif statement.kind is NodeType.RETURN_STATEMENT:
        find_references_expression(statement.expression, symbol_table, debug)

    elif statement.kind is NodeType.WRITE_STATEMENT:
        find_references_expression(statement.expression, symbol_table, debug)

    elif statement.kind is NodeType.WRITELN_STATEMENT:
        pass

    elif statement.kind is NodeType.IF_STATEMENT:
        find_references_expression(statement.condition, symbol_table, debug)
        find_references_statement(statement.statement, symbol_table, debug)
        if statement.else_statement is not None:
            find_references_statement(statement.else_statement, symbol_table, debug)

    elif statement.kind is NodeType.CMPND_STATEMENT:
        local_variables = {}
        dec = statement.local_declarations
        while dec is not None:
            if dec.kind not in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
                raise TypeCheckerException(dec.line_number, 'Local declaration is not a variable, pointer, or array.')
            local_variables[dec.name] = dec
            dec = dec.next_node

        symbol_table.append(local_variables)
        stmnt = statement.statements # I regret my chosen variable names
        while stmnt is not None:
            find_references_statement(stmnt, symbol_table, debug)
            stmnt = stmnt.next_node
        symbol_table.pop()

    else:
        raise TypeCheckerException(statement.line_number, 'Statement node is not a valid type of statement.')

def find_references_expression(expression, symbol_table, debug):
    if expression.kind in (NodeType.VAR_EXP, NodeType.ARRAY_EXP):
        dec = lookup(expression.name, symbol_table)
        if dec is None:
            raise TypeCheckerException(
                    expression.line_number, 
                    'Undeclared variable or array with name {}.'.format(expression.name)
            )
        expression.declaration = dec
        if debug:
            print '{} {} on line {} linked to declaration on line {}.'.format(
                    'Variable' if expression.kind is NodeType.VAR_EXP else 'Array',
                    expression.name,
                    expression.line_number,
                    dec.line_number
            )

    elif expression.kind is NodeType.FUN_CALL_EXP:
        if expression.name not in symbol_table[0]:
            raise TypeCheckerException(
                    expression.line_number, 
                    'Undeclared function with name {}.'.format(expression.name)
            )

        expression.declaration = symbol_table[0][expression.name]
        if debug:
            print 'Function call {} on line {} linked to declaration on line {}.'.format(
                    expression.name,
                    expression.line_number,
                    expression.declaration.line_number
            )

        arg = expression.arguments
        while arg is not None:
            find_references_expression(arg, symbol_table, debug)
            arg = arg.next_node
    
    elif expression.kind in (NodeType.ASSIGN_EXP, NodeType.COMP_EXP, NodeType.MATH_EXP):
        find_references_expression(expression.left, symbol_table, debug)
        find_references_expression(expression.right, symbol_table, debug)

    elif expression.kind in (NodeType.ADDRESS_EXP, NodeType.DEREF_EXP, NodeType.NEG_EXP):
        find_references_expression(expression.expression, symbol_table, debug) # again, regretting my chosen variable names
    
    elif expression.kind in (NodeType.NUM_EXP, NodeType.STR_EXP, NodeType.READ_EXP):
        pass

    else:
        raise TypeCheckerException(expression.line_number, 'Expression node is not a valid type of expression.')

def type_check_declarations(parse_tree, debug):
    declaration = parse_tree
    while declaration is not None:
        if declaration.kind in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
            if declaration.type_token.kind is TokenType.T_VOID:
                raise TypeCheckerException(declaration.line_number, 'Cannot have a variable or array of type "void".')
            declaration = declaration.next_node

        elif declaration.kind is NodeType.FUN_DEC:
            """
            raise TypeCheckerException(declaration.line_number, 'Function {} has a return type of {}, but returns {}.'.format(
                declaration.name,
                TokenType.names[declaration.type_token.kind],
                return_type
            ))
            """
            type_check_statement(declaration.body, declaration.type_token.kind, debug)
            declaration = declaration.next_node

        else:
            raise TypeCheckerException(declaration.line_number, 'Top-level declaration is not a variable, pointer, array, or function.')

def type_check_statement(statement, return_type, debug):
    if statement.kind is NodeType.EXP_STATEMENT:
        type_check_expression(statement.expression, debug)

    elif statement.kind is NodeType.WHILE_STATEMENT:
        type_check_expression(statement.condition, debug)
        if statement.condition.type_string is not 'int':
            raise TypeCheckerException(statement.line_number, 'Type of while condition is "{}", but should be "int".'.format(statement.condition.type_string))
        type_check_statement(statement.statement, return_type, debug)

    elif statement.kind is NodeType.RETURN_STATEMENT:
        type_check_expression(statement.expression, debug)
        if return_type is TokenType.T_INT:
            if statement.expression.type_string is not 'int':
                raise TypeCheckerException(statement.line_number, 'Function has a return type of int, but returns {}.'.format(statement.expression.type_string))
        elif return_type is TokenType.T_STRING:
            if statement.expression.type_string is not 'string':
                raise TypeCheckerException(statement.line_number, 'Function has a return type of string, but returns {}.'.format(statement.expression.type_string))
        else:
            raise TypeCheckerException(statement.line_number, 'Function has a return type of void, but returns {}.'.format(statement.expression.type_string))

    elif statement.kind is NodeType.WRITE_STATEMENT:
        type_check_expression(statement.expression, debug)

    elif statement.kind is NodeType.WRITELN_STATEMENT:
        pass

    elif statement.kind is NodeType.IF_STATEMENT:
        type_check_expression(statement.condition, debug)
        if statement.condition.type_string is not 'int':
            raise TypeCheckerException(statement.line_number, 'Type of if condition is "{}", but should be "int".'.format(statement.condition.type_string))
        type_check_statement(statement.statement, return_type, debug)
        type_check_statement(statement.else_statement, return_type, debug)

    elif statement.kind is NodeType.CMPND_STATEMENT:
        dec = statement.local_declarations
        while dec is not None:
            if dec.type_token.kind is TokenType.T_VOID:
                raise TypeCheckerException(dec.line_number, 'Cannot have a variable or array of type "void".')

        stmnt = statement.statements 
        while stmnt is not None:
            type_check_statement(stmnt, return_type, debug)
            stmnt = stmnt.next_node

    else:
        raise TypeCheckerException(statement.line_number, 'Statement node is not a valid type of statement.')

def type_check_expression(expression, debug):
    if expression.kind is NodeType.VAR_EXP:
        if expression.declaration.type_token.kind is TokenType.T_INT:
            if expression.declaration.is_pointer:
                expression.type_string = 'pointer to int'
            else:
                expression.type_string = 'int'
        elif expression.declaration.type_token.kind is TokenType.T_STRING:
            if expression.declaration.is_pointer:
                expression.type_string = 'pointer to string'
            else:
                expression.type_string = 'string'
        else:
            raise TypeCheckerException(expression.line_number, 'Cannot have a variable of type "void".')

    elif expression.kind is NodeType.ARRAY_EXP:
        if expression.declaration.kind is not NodeType.ARRAY_DEC:
            raise TypeCheckerException(expression.line_number, 'Cannot take an element reference of a non-array.')
        type_check_expression(expression.expression, debug)
        if expression.expression.type_string != 'int':
            raise TypeCheckerException(expression.line_number, 'Array element reference expression must be of type "int".')
        if expression.declaration.type_token.kind is TokenType.T_INT:
            expression.type_string = 'int'
        elif expression.declaration.type_token.kind is TokenType.T_STRING:
            expression.type_string = 'string'
        else:
            raise TypeCheckerException(expression.line_number, 'Cannot have an array of type "void".')
    
    elif expression.kind is NodeType.FUN_CALL_EXP:
        pass
    
    elif expression.kind is NodeType.ASSIGN_EXP:
        pass

    elif expression.kind is NodeType.COMP_EXP:
        type_check_expression(expression.left, debug)
        type_check_expression(expression.right, debug)
        if expression.left.type_string == expression.right.type_string:
            raise TypeCheckerException(expression.line_number, 'Left side of comparison expression has type "{}", but right side has type "{}".'.format(
                expression.left.type_string,
                expression.right.type_string
                )
            )
        expression.type_string = expression.left.type_string

    elif expression.kind is NodeType.MATH_EXP:
        type_check_expression(expression.left, debug)
        type_check_expression(expression.right, debug)
        if expression.left.type_string != 'int':
            raise TypeCheckerException(expression.line_number, 'Left side of arithmetic expression has type "{}", but should have type "int".'.format(
                expression.left.type_string
                )
            )

        if expression.right.type_string != 'int':
            raise TypeCheckerException(expression.line_number, 'Right side of arithmetic expression has type "{}", but should have type "int".'.format(
                expression.right.type_string
                )
            )
        expression.type_string = 'int' 

    elif expression.kind is NodeType.ADDRESS_EXP:
        type_check_expression(expression.expression, debug)
        if expression.expression.kind not in (NodeType.VAR_EXP, NodeType.ARRAY_EXP):
            raise TypeCheckerException(expression.line_number, 'Can only take the address of a variable or array element.')
        expression.type_string = 'int'

    elif expression.kind is NodeType.DEREF_EXP:
        type_check_expression(expression.expression, debug)
        if expression.expression.type_string == 'pointer to int':
            expression.type_string = 'int'
        elif expression.expression.type_string == 'pointer to string':
            expression.type_string = 'string'
        else:
            raise TypeCheckerException(expression.line_number, 'Can only dereference pointers to integers or strings.')

    elif expression.kind is NodeType.NEG_EXP:
        type_check_expression(expression.expression, debug)
        if expression.expression.type_string != 'int':
            raise TypeCheckerException(expression.line_number, 'Cannot take the negative of a non-integer value.')
        expression.type_string = 'int'
    
    elif expression.kind in (NodeType.NUM_EXP, NodeType.READ_EXP):
        expression.type_string = 'int'

    elif expression.kind is NodeType.STR_EXP:
        expression.type_string = 'string'

    else:
        raise TypeCheckerException(expression.line_number, 'Expression node is not a valid type of expression.')
