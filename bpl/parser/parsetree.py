"""
AUTHOR: Oren Shoham
DATE: March 2, 2014

Parse Tree node classes for the BPL Parser. Implemented for CS331 at Oberlin College.
"""

from bpl.scanner.token import TokenType, Token, enum

NodeType = enum('VAR_DEC',
        'FUN_DEC',
        'ARRAY_DEC',
        'VAR_EXP',
        'EXP_STATEMENT',
        'CMPND_STATEMENT',
        'STATEMENT',
        'EXPRESSION')

def str_if_not_none(x):
    """Return str(x) if x is not None. Otherwise, return the empty string."""
    string = ''
    if x is not None:
        string += '\n{}'.format(str(x))
    return string

class TreeNode(object):
    def __init__(self, kind, line_number, next_node=None):
        self.kind = getattr(NodeType, kind)
        self.line_number = line_number
        self.next_node = next_node
        self.base_string = 'Line {}: {}'.format(
                self.line_number,
                self.__class__.__name__
        )


class DecNode(TreeNode):
    def __init__(self, kind, line_number, name, type_token, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)
        self.name = name
        self.type_token = type_token

class VarDecNode(DecNode):
    def __init__(self, kind, line_number, name, type_token, is_pointer = False, next_node = None):
        DecNode.__init__(self, kind, line_number, name, type_token, next_node)
        self.is_pointer = is_pointer

    def __str__(self):
        string = '{} id = {} type = {}{}'.format(
                self.base_string,
                self.name,
                self.type_token.kind,
                str_if_not_none(self.next_node)
        )
        return string

class FunDecNode(DecNode):
    def __init__(self, kind, line_number, name, type_token, params, body, next_node = None):
        DecNode.__init__(self, kind, line_number, name, type_token, next_node)
        self.params = params
        self.body = body

    def __str__(self):
        string = '{} id = {} return type = {}\n\tparams: {}\n\tbody: {}{}'.format(
                self.base_string,
                self.name,
                self.type_token.kind,
                str(self.params),
                str(self.body),
                str_if_not_none(self.next_node)
        )
        return string

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

    def __str__(self):
        string = '{}\n{}{}'.format(
                self.base_string,
                str(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class CompoundStatementNode(StatementNode):
    def __init__(self, kind, line_number, local_declarations, statements, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.local_declarations = local_declarations
        self.statements = statements

    def __str__(self):
        string = '{}{}{}{}'.format(
                self.base_string,
                str_if_not_none(self.local_declarations),
                str_if_not_none(self.statements),
                str_if_not_none(self.next_node)
        )
        return string

class ExpressionNode(TreeNode):
    def __init__(self, kind, line_number, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)

class VariableNode(ExpressionNode):
    def __init__(self, kind, line_number, name, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.name = name

    def __str__(self):
        string = '{} id = {}{}'.format(
                self.base_string,
                self.name,
                str_if_not_none(self.next_node)
        )
        return string
