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
        self.symbol_table = [{}]

    def add_decs_to_symbol_table(self):
        declaration = self.parse_tree
        while declaration is not None:
            if declaration.kind in (NodeType.VAR_DEC, NodeType.ARRAY_DEC):
                self.symbol_table[0][declaration.name] = declaration
                declaration = declaration.next_node

            elif declaration.kind is NodeType.FUN_DEC:
                declaration = declaration.next_node

            else:
                pass
