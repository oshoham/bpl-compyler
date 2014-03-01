"""
AUTHOR: Oren Shoham
DATE: Feb. 16, 2014

A Parser for the BPL programming language. Implemented for CS331 at Oberlin College.
"""

from bpl.scanner.scanner import Scanner
from bpl.scanner.token import TokenType, Token, is_type_token

NodeType = enum('VAR_DEC',
        'FUN_DEC',
        'ARRAY_DEC',
        'STATEMENT',
        'EXPRESSION')

class TreeNode(object):
    def __init__(self, kind, line_number, next_node=None):
        self.kind = getattr(NodeType, kind)
        self.line_number = line_number
        self.next_node = next_node

class DecNode(TreeNode):
    def __init__(self, kind, line_number, name, type_token, next_node = None):
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
            raise ParserException('Parser error on line {}: {}'.format(
                self.scanner.line_number,
                message))
        self.scanner.get_next_token()
        return current_token

    def declaration_list(self):
        d = declaration()
        head = d
        while self.scanner.next_token.kind != TokenType.T_EOF:
            d1 = declaration()
            d.next_dec = d1
            d = d1
        return head

    def declaration(self, local=False):
        is_pointer = False
        line_number = self.scanner.line_number
        if not is_type_token(self.scanner.next_token):
            raise ParserException('Error on line {}: Expected a type token to begin a declaration.'.format(line_number))
        type_token = self.scanner.next_token
        self.scanner.get_next_token()

        if self.scanner.next_token.kind == TokenType.T_MULT:
            is_pointer = True
            self.scanner.get_next_token()
        
        id_token = self.expect('T_ID', 'Expected an identifier as part of the declaration.')

        # handle variable declarations
        if self.scanner.next_token.kind == TokenType.T_SEMICOLON:
           self.scanner.get_next_token() 
           return VarDecNode('VAR_DEC', line_number, id_token.value, type_token, is_pointer)

        # handle array declarations
        elif self.scanner.next_token.kind == TokenType.T_LBRACKET:
            self.scanner.get_next_token()
            size = int(self.expect('T_NUM', 'Expected an integer size as part of the array declaration.').value)
            self.expect('T_RBRACKET', 'Expected a right bracket as part of the array declaration.')
            self.expect('T_SEMICOLON', 'Expected a semicolon to end the array declaration.')
            return ArrayDecNode('ARRAY_DEC', line_number, id_token.value, type_token, size, is_pointer)

        # handle function delcarations
        elif self.scanner.next_token.kind == TokenType.T_LPAREN:
            if is_pointer:
                raise ParserException('Error on line {}: Cannot declare a pointer to a function.'.format(line_number))
            if local:
                raise ParserException('Error on line {}: Cannot declare a function inside a compound statement.'.format(line_number))
            self.scanner.get_next_token()
            parameters = self.params()
            self.expect('T_RPAREN', 'Expected a right parenthesis to end the function parameter declarations.')
            body = self.compound_statement()
            return FunDecNode('FUN_DEC', line_number, id_token.value, type_token, params, body)

        else:
            raise ParserException('Error on line {}: Unexpected token in declaration.'.format(line_number))
