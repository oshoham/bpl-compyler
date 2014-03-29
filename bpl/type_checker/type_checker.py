"""
AUTHOR: Oren Shoham
DATE: long ago in a distant land...
"""

from bpl.parser.parsetree import *

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
        raise TypeCheckerException(statement.line_number, 'Expression node is not a valid type of expression.')

def type_check_top_level(parse_tree, debug):
    declaration = parse_tree
    while declaration is not None:
        if declaration.kind in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
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

    elif statement.kind is NodeType.WHILE_STATEMENT:

    elif statement.kind is NodeType.RETURN_STATEMENT:

    elif statement.kind is NodeType.WRITE_STATEMENT:

    elif statement.kind is NodeType.WRITELN_STATEMENT:
        pass

    elif statement.kind is NodeType.IF_STATEMENT:

    elif statement.kind is NodeType.CMPND_STATEMENT:

    else:
        raise TypeCheckerException(statement.line_number, 'Statement node is not a valid type of statement.')
