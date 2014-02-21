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
    def __init__(self, kind, line_number):
        self.kind = getattr(NodeType, kind)
        self.line_number = line_number

class DecNode(TreeNode):
    def __init__(self, kind, line_number, next_dec)
        TreeNode.__init__(self, kind, line_number)
        self.next_dec = next_dec

class VarDecNode(DecNode):
    def __init__(self, kind, line_number, next_dec, token_type, is_pointer = False):
        DecNode.__init__(self, kind, line_number, next_dec)
        self.token_type = token_type
        self.is_pointer = is_pointer

class FunDecNode(DecNode):
    def __init__(self, kind, line_number, next_dec, return_type, params, body):
        DecNode.__init__(self, kind, line_number, next_dec)
        self.return_type = return_type
        self.params = params
        self.body = body

class ArrayDecNode(VarDecNode):
    def __init__(self, kind, line_number, next_dec, token_type, is_pointer = False, size):
        VarDecNode.__init__(self, kind, line_number, next_dec, token_type, is_pointer)
        self.size = size

class StatementNode(TreeNode):
    def __init__(self, kind, line_number, next_statement):
        TreeNode.__init__(self, kind, line_number)
        self.next_statement = next_statement

class ExpressionStatement(StatementNode):
    def __init__(self, kind, line_number, next_statement):
        StatementNode.__init__(self, kind, line_number, next_statement)

class ParserException(Exception):
    pass

class Parser(object):

    def __init__(self, input_file):
        self.scanner = Scanner(input_file)
        self.scanner.next_token = scanner.get_next_token()

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
