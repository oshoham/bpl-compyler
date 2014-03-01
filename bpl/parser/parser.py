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

class ExpressionStatementNode(StatementNode):
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
    def __init__(self, line_number, message):
        message = 'Error on line {}: {}'.format(line_number, message)
        Exception.__init__(self, message)

class Parser(object):

    def __init__(self, input_file):
        """Initialize a Scanner using 'input_file' and set its current token to the first token in 'input_file'."""
        self.scanner = Scanner(input_file)
        self.scanner.get_next_token()

    def parse(self):
        """Attempt to parse the Parser's input file, catching ParserExceptions."""
        try:
            parse_tree = self.program()
        except ParserException as p:
            print p.message
        return parse_tree

    def program(self):
        """Return a complete parse tree."""
        return self.statement()

    def expect(self, token, message):
        """Consume the current token, raising an error if it is not of the expected type."""
        current_token = self.scanner.next_token
        if current_token.kind != getattr(TokenType, token):
            raise ParserException(self.scanner.line_number, message)
        self.scanner.get_next_token()
        return current_token

    def declaration_list(self):
        """Return a linked list of declaration nodes."""
        d = declaration()
        head = d
        while self.scanner.next_token.kind != TokenType.T_EOF:
            d1 = declaration()
            d.next_dec = d1
            d = d1
        return head

    def declaration(self, local=False):
        """Return a single variable, array, or function declaration node."""
        is_pointer = False
        line_number = self.scanner.line_number
        if not is_type_token(self.scanner.next_token):
            raise ParserException(line_number, 'Expected a type token to begin a declaration.')
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
                raise ParserException(line_number, 'Cannot declare a pointer to a function.')
            if local:
                raise ParserException(line_number, 'Cannot declare a function inside a compound statement.')
            self.scanner.get_next_token()
            parameters = self.params()
            self.expect('T_RPAREN', 'Expected a right parenthesis to end the function parameter declarations.')
            body = self.compound_statement()
            return FunDecNode('FUN_DEC', line_number, id_token.value, type_token, params, body)

        else:
            raise ParserException(line_number, 'Unexpected token in declaration.')

    def statement(self):
        """Return a single statement node, which can be one of many types."""
        if self.scanner.next_token.kind == TokenType.T_LBRACE:
            return self.compound_statement()
        elif self.scanner.next_token.kind == TokenType.T_IF:
            return self.if_statement()
        elif self.scanner.next_token.kind == TokenType.T_WHILE:
            return self.while_statement()
        elif self.scanner.next_token.kind == TokenType.T_RETURN:
            return self.return_statement()
        elif self.scanner.next_token.kind == TokenType.T_WRITE or \
                self.scanner.next_token.kind == TokenType.T_WRITELN:
            return self.write_statement()
        else:
            return self.expression_statement()

    def expression_statement(self):
        """Return an expression statement node that points to an expression node."""
        exp = None
        line_number = self.scanner.line_number
        if self.scanner.next_token.kind != TokenType.T_SEMICOLON:
            exp = self.expression()
        self.expect('T_SEMICOLON', 'Expected a semicolon to end the expression.')
        return ExpressionStatementNode('EXP_STATEMENT', line_number, expression)

    def expression(self):
        """Return a single expression node."""
        line_number = self.scanner.line_number
        id_token = self.expect('T_ID', 'Expected an identifier as part of the variable expression.')
        return VarExpNode('VAR_EXP', line_number, id_token.value)
