"""
AUTHOR: Oren Shoham
DATE: March 2, 2014

Parse Tree node classes for the BPL Parser. Implemented for CS331 at Oberlin College.
"""

from bpl.scanner.token import TokenType, Token, enum

NodeType = enum('VAR_DEC',
        'FUN_DEC',
        'ARRAY_DEC',
        'EXP_STATEMENT',
        'CMPND_STATEMENT',
        'WHILE_STATEMENT',
        'RETURN_STATEMENT',
        'IF_STATEMENT',
        'WRITE_STATEMENT',
        'WRITELN_STATEMENT',
        'VAR_EXP',
        'ASSIGN_EXP',
        'COMP_EXP',
        'ARRAY_EXP',
        'ADDRESS_EXP',
        'DEREF_EXP',
        'FUN_CALL_EXP',
        'MATH_EXP',
        'NEG_EXP',
        'NUM_EXP',
        'STR_EXP',
        'READ_EXP',
)

class TreeNode(object):
    """Base class for parse tree nodes. Inherited by more specific subclasses of nodes."""
    def __init__(self, kind, line_number, next_node=None):
        self.kind = getattr(NodeType, kind)
        self.line_number = line_number
        self.next_node = next_node
        self.base_string = 'Line {}: {}'.format(
                self.line_number,
                self.__class__.__name__
        )

class DecNode(TreeNode):
    """Base class for declaration nodes. Inherited by VarDecNode, FunDecNode, and ArrayDecNode."""
    def __init__(self, kind, line_number, name, type_token, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)
        self.name = name
        self.type_token = type_token

class VarDecNode(DecNode):
    """Represents a variable declaration."""
    def __init__(self, kind, line_number, name, type_token, is_pointer = False, next_node = None):
        DecNode.__init__(self, kind, line_number, name, type_token, next_node)
        self.is_pointer = is_pointer

    def __str__(self):
        string = '{}{} id = {} type = {}{}'.format(
                self.base_string,
                ' (pointer)' if self.is_pointer else '',
                self.name,
                self.type_token.kind,
                str_if_not_none(self.next_node)
        )
        return string

class FunDecNode(DecNode):
    """Represents a function declaration."""
    def __init__(self, kind, line_number, name, type_token, params, body, next_node = None):
        DecNode.__init__(self, kind, line_number, name, type_token, next_node)
        self.params = params
        self.body = body

    def __str__(self):
        string = '{} id = {} return type = {}\nParams:\n{}{}Body:\n{}{}'.format(
                self.base_string,
                self.name,
                self.type_token.kind,
                indent(self.params),
                '\n' if self.params is not None else '',
                indent(self.body),
                str_if_not_none(self.next_node)
        )
        return string

class ArrayDecNode(VarDecNode):
    """Represents an array declaration."""
    def __init__(self, kind, line_number, name, type_token, size, is_pointer = False, next_node = None):
        VarDecNode.__init__(self, kind, line_number, name, type_token, is_pointer, next_node)
        self.size = size

    def __str__(self):
        string = '{}{} id = {} type = {} size = {}{}'.format(
                self.base_string,
                ' (pointer)' if self.is_pointer else '',
                self.name,
                self.type_token.kind,
                str(self.size),
                str_if_not_none(self.next_node)
        )
        return string

class StatementNode(TreeNode):
    def __init__(self, kind, line_number, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)

class ExpressionStatementNode(StatementNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

    def __str__(self):
        string = '{}\nExpression:\n{}{}'.format(
                self.base_string,
                indent(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class CompoundStatementNode(StatementNode):
    def __init__(self, kind, line_number, local_declarations, statements, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.local_declarations = local_declarations
        self.statements = statements

    def __str__(self):
        string = '{}\nLocal Declarations:\n{}{}Statements:\n{}{}'.format(
                self.base_string,
                indent(self.local_declarations),
                '\n' if self.local_declarations is not None else '',
                indent(self.statements),
                str_if_not_none(self.next_node)
        )
        return string

class WhileStatementNode(StatementNode):
    def __init__(self, kind, line_number, condition, statement, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.condition = condition
        self.statement = statement

    def __str__(self):
        string = '{}\nCondition:\n{}\nStatement:\n{}{}'.format(
                self.base_string,
                indent(self.condition),
                indent(self.statement),
                str_if_not_none(self.next_node)
        )
        return string

class ReturnStatementNode(StatementNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

    def __str__(self):
        string = '{}{}{}{}'.format(
                self.base_string,
                '\nExpression:\n' if self.expression is not None else '',
                indent(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class IfStatementNode(StatementNode):
    def __init__(self, kind, line_number, condition, statement, else_statement, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.condition = condition
        self.statement = statement
        self.else_statement = else_statement

    def __str__(self):
        string = '{}\nCondition:\n{}\nStatement:\n{}{}{}{}'.format(
                self.base_string,
                indent(self.condition),
                indent(self.statement),
                '\nElse Statement:\n' if self.else_statement is not None else '',
                indent(self.else_statement),
                str_if_not_none(self.next_node)
        )
        return string

class WriteStatementNode(StatementNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

    def __str__(self):
        string = '{}\nExpression:\n{}{}'.format(
                self.base_string,
                indent(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class WritelnStatementNode(StatementNode):
    def __init__(self, kind, line_number, next_node = None):
        StatementNode.__init__(self, kind, line_number, next_node)

    def __str__(self):
        string = '{}{}'.format(
                self.base_string,
                str_if_not_none(self.next_node)
        )
        return string

class ExpressionNode(TreeNode):
    def __init__(self, kind, line_number, next_node = None):
        TreeNode.__init__(self, kind, line_number, next_node)

class VarExpNode(ExpressionNode):
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

class OpNode(ExpressionNode):
    def __init__(self, kind, line_number, token, left, right, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.token = token
        self.left = left
        self.right = right

    def __str__(self):
        string = '{} token = {} ({})\nLeft:\n{}\nRight:\n{}{}'.format(
                self.base_string,
                self.token.kind,
                TokenType.names[self.token.kind],
                indent(self.left),
                indent(self.right),
                str_if_not_none(self.next_node)
        ) 
        return string

class ArrayExpNode(VarExpNode):
    def __init__(self, kind, line_number, name, expression, next_node = None):
        VarExpNode.__init__(self, kind, line_number, name, next_node)
        self.expression = expression

    def __str__(self):
        string = '{} id = {}\n\texpression: {}{}'.format(
                self.base_string,
                self.name,
                str(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class DerefExpNode(ExpressionNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

    def __str__(self):
        string = '{}\n\texpression: {}{}'.format(
                self.base_string,
                str(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class AddressExpNode(ExpressionNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

    def __str__(self):
        string = '{}\n\texpression: {}{}'.format(
                self.base_string,
                str(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class NegExpNode(ExpressionNode):
    def __init__(self, kind, line_number, expression, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.expression = expression

    def __str__(self):
        string = '{}\n\texpression: {}{}'.format(
                self.base_string,
                str(self.expression),
                str_if_not_none(self.next_node)
        )
        return string

class NumExpNode(ExpressionNode):
    def __init__(self, kind, line_number, number, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.number = number
    
    def __str__(self):
        string = '{} number = {}{}'.format(
                self.base_string,
                self.number,
                str_if_not_none(self.next_node)
        )
        return string

class StringExpNode(ExpressionNode):
    def __init__(self, kind, line_number, string, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.string = string
    
    def __str__(self):
        string = '{} string = {}{}'.format(
                self.base_string,
                self.string,
                str_if_not_none(self.next_node)
        )
        return string

class ReadExpNode(ExpressionNode):
    def __init__(self, kind, line_number, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)

    def __str__(self):
        return self.base_string

class FunCallExpNode(ExpressionNode):
    def __init__(self, kind, line_number, name, arguments, next_node = None):
        ExpressionNode.__init__(self, kind, line_number, next_node)
        self.name = name
        self.arguments = arguments

    def __str__(self):
        string = '{} name = {}\n\tparams:{}{}'.format(
                self.base_string,
                self.name,
                str_if_not_none(self.arguments),
                str_if_not_none(self.next_node)
        )
        return string

def str_if_not_none(x):
    """Return str(x) if x is not None. Otherwise, return an empty string."""
    string = ''
    if x is not None:
        string += '\n{}'.format(str(x))
    return string

def indent(s):
    indented_string = ''
    if s is None:
        return indented_string
    for line in str(s).splitlines():
        indented_string += '| {}\n'.format(line)
    return indented_string[:-1]
