# Hacking together an Enum data type.
def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

# An "Enum" that enumerates all possible kinds of Tokens
TokenType = enum('T_ID',
        'T_NUM',
        'T_INT',
        'T_VOID',
        'T_STRING',
        'T_IF',
        'T_ELSE',
        'T_WHILE',
        'T_RETURN',
        'T_WRITE',
        'T_WRITELN',
        'T_READ',
        'T_SEMICOLON',
        'T_COMMA',
        'T_LBRACKET',
        'T_RBRACKET', 
        'T_LBRACE', 
        'T_RBRACE',
        'T_LPAREN',
        'T_RPAREN',
        'T_LESS',
        'T_LEQ',
        'T_EQ',
        'T_NEQ',
        'T_GEQ',
        'T_GREATER',
        'T_PLUS',
        'T_MINUS',
        'T_MULT',
        'T_DIV',
        'T_MOD',
        'T_AND',
        'T_EOF')

class Token:

    # kind should be a string that is a valid TokenType (see above)
    # value should be a string
    # line_number should be an integer
    def __init__(self, kind, value, line_number):
        self.kind = getattr(TokenType, kind)
        self.value = value
        self.line_number = line_number

class Scanner:
    
    def __init__(self, file_name):
