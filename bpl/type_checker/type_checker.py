"""
AUTHOR: Oren Shoham
DATE: long ago in a distant land...
"""

from bpl.parser.parsetree import *
from bpl.parser.parser import *

class TypeCheckerException(Exception):
    def __init__(self, line_number, message):
        message = 'Type Checking Error on line {}: {}'.format(line_number, message)
        Exception.__init__(self, message)

class TypeChecker(object):

    def __init__(self, input_file):
        parser = Parser(input_file)
        self.parse_tree = parser.parse()
        self.symbol_table = [{}] # this is meant to function as a stack of symbol tables

    def lookup(self, symbol):
        """Check whether symbol is a key in any of the dictionaries in symbol table, starting at the top of stack.

        Return the parse tree node that is the value of symbol if symbol is a valid key, otherwise None.
        """
        for scope in reversed(range(len(self.symbol_table))):
            if symbol in self.symbol_table[scope]
                return self.symbol_table[scope][symbol]
        return None

    def find_references(self):
        """Iterate through the top-level declarations of the parse tree and create links between expressions and their declarations."""
        declaration = self.parse_tree
        while declaration is not None:
            if declaration.kind in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
                self.symbol_table[0][declaration.name] = declaration
                declaration = declaration.next_node

            elif declaration.kind is NodeType.FUN_DEC:
                local_variables = {}
                param = declaration.params
                while param is not None:
                    # do some stuff
                    if param.kind not in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
                        raise TypeCheckerException(param.line_number, 'Function parameter is not a variable, pointer, or array.')
                    local_variables[param.name] = param
                    param = param.next_node

                self.symbol_table.append(local_variables) # push local variables onto the symbol table stack
                self.find_references_statement(declaration.body)
                self.symbol_table.pop() # pop local variables off of the symbol table stack
                declaration = declaration.next_node

            else:
                raise TypeCheckerException(declaration.line_number, 'Top-level declaration is not a variable, pointer, array, or function.')
    
    def find_references_statement(self, statement):
        """Create links between expressions associated with a statement and their declarations in the symbol table."""
        if statement.kind is NodeType.EXP_STATEMENT:
            self.find_references_expression(statement.expression)

        elif statement.kind is NodeType.WHILE_STATEMENT:
            self.find_references_expression(statement.condition)
            self.find_references_statement(statement.statement)

        elif statement.kind is NodeType.RETURN_STATEMENT:
            self.find_references_expression(statement.expression)

        elif statement.kind is NodeType.WRITE_STATEMENT:
            self.find_references_expression(statement.expression)

        elif statement.kind is NodeType.WRITELN_STATEMENT:
            pass

        elif statement.kind is NodeType.IF_STATEMENT:
            self.find_references_expression(statement.condition)
            self.find_references_statement(statement.statement)
            if statement.else_statement not None:
                self.find_references_statement(statement.else_statement)

        elif statement.kind is NodeType.CMPND_STATEMENT:
            local_variables = {}
            dec = statement.local_declarations
            while dec is not None:
                if dec.kind not in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
                    raise TypeCheckerException(dec.line_number, 'Local declaration is not a variable, pointer, or array.')
                local_variables[dec.name]
                dec = dec.next_node

            self.symbol_table.append(local_variables)
            stmnt = statement.statements # I regret my chosen variable names
            while stmnt is not None:
                find_references_statement(stmnt)
            self.symbol_table.pop()

        else:
            raise TypeCheckerException(statement.line_number, 'Statement node is not a valid type of statement.')

    def find_references_expression(self, expression):
        if expression.kind in (NodeType.VAR_EXP, NodeType.ARRAY_EXP):
            dec = self.lookup(expression.name)
            if dec is None:
                raise TypeCheckerException(
                        expression.line_number, 
                        'Undeclared variable or array with name {}.'.format(expression.name)
                )
            expression.declaration = dec

        elif expression.kind is NodeType.FUN_CALL_EXP:
            if expression.name not in self.symbol_table[0]
                raise TypeCheckerException(
                        expression.line_number, 
                        'Undeclared function with name {}.'.format(expression.name)
                )
            expression.declaration = self.symbol_table[0][expression.name]

            arg = expression.arguments
            while arg is not None
                self.find_references_expression(arg)
                arg = arg.next_node
        
        elif expression.kind in (NodeType.ASSIGN_EXP, NodeType.COMP_EXP, NodeType.MATH_EXP):
            self.find_references_expression(expression.left)
            self.find_references_expression(expression.right)

        elif expression.kind in (NodeType.ADDRESS_EXP, NodeType.DEREF_EXP, NodeType.NEG_EXP):
            self.find_references_expression(expression.expression) # again, regretting my chosen variable names
        
        elif expression.kind in (NodeType.NUM_EXP, NodeType.NodeType.STR_EXP, NodeType.READ_EXP):
            pass

        else:
            raise TypeCheckerException(statement.line_number, 'Expression node is not a valid type of expression.')
