"""
AUTHOR: Oren Shoham
DATE: Feb. 16, 2014

A Parser for the BPL programming language. Implemented for CS331 at Oberlin College.
"""

from bpl.scanner.scanner import Scanner
from bpl.scanner.token import TokenType, Token, is_type_token

NodeType = enum('DECLARATION',
        'STATEMENT',
        'EXPRESSION')

class TreeNode(object):
    def __init__(self, kind, line_number, next_node=None):
        self.kind = getattr(NodeType, kind)
        self.line_number = line_number
        self.next_node = next_node

class DecNode(TreeNode):
    def __init__(self, kind, line_number, name, type_token, next_node = None)
        TreeNode.__init__(self, kind, line_number, next_node)
        self.name = name
        self.type_token = type_token

class VarDecNode(DecNode):
    def __init__(self, kind, line_number, name, type_token, is_pointer = False, next_node = None):
        DecNode.__init__(self, kind, line_number, name, type_token, next_node)
        self.is_pointer = is_pointer

class FunDecNode(DecNode):
    def __init__(self, kind, line_number, name, type_token, params, body, next_node = None):
        DecNode.__init__(self, kind, line_number, name, type_token, next_node)
        self.params = params
        self.body = body

class ArrayDecNode(VarDecNode):
    def __init__(self, kind, line_number, name, type_token, size, is_pointer = False, next_node = None):
        VarDecNode.__init__(self, kind, line_number, name, type_token, is_pointer, next_node)
        self.size = size

class StatementNode(TreeNode):
    def __init__(self, kind, line_number, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)

class ExpressionStatement(StatementNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

class ExpressionNode(TreeNode):
    def __init__(self, kind, line_number, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)

class VarExpNode(ExpressionNode):
    def __init__(self, kind, line_number, name, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.name = name

class ParserException(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class Parser(object):

    def __init__(self, input_file):
        self.scanner = Scanner(input_file)
        self.scanner.next_token = scanner.get_next_token()

    def expect(self, token, message):
        current_token = self.scanner.next_token
        if current_token.kind != getattr(TokenType, token):
            raise ParserException(message)
        self.scanner.get_next_token()


    def declaration_list(self):
        d = declaration()
        head = d
        while self.scanner.next_token.kind != TokenType.T_EOF:
            d1 = declaration()
            d.next_dec = d1
            d = d1
        return head

    def declaration(self):
        if not is_type_token(self.scanner.next_token):
            raise ParserException()
        type_token = self.scanner.next_token
