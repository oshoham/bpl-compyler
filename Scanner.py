# Hacking together an Enum data type
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
        'T_ASSIGN',
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

    def __str__(self):
        return "Token " + str(self.kind) + ", string " + self.value + ", line number " + str(self.line_number)

class Scanner:

    def __init__(self, file_name):
        self.input_file = open(file_name)
        self.current_line = self.input_file.readline()
        self.line_number = 1
        self.next_token = None
        self.keywords = ["int", "void", "string", "if", "else", "while",
                "return", "write", "writeln", "read"]
        keyword_tokens = ['T_INT', 'T_VOID', 'T_STRING', 'T_IF', 'T_ELSE',
                'T_WHILE', 'T_RETURN', 'T_WRITE', 'T_WRITELN', 'T_READ']
        self.keyword_hash = dict(zip(self.keywords, keyword_tokens)) 

    def get_next_token(self):
        i = 0
        while(i < len(self.current_line) and self.current_line[i].isspace()):
            i += 1
        if(i == len(self.current_line)):
            self.current_line = self.input_file.readline()
            if not self.current_line:
                self.next_token = Token('T_EOF', "", self.line_number)
                self.input_file.close()
            else:
                self.line_number += 1
                self.get_next_token()
        else: # i < len(self.current_line)
            if(self.current_line[i].isdigit()):
                j = i+1
                while(j < len(self.current_line) and self.current_line[j].isdigit()):
                    j += 1
                token_string = self.current_line[i:j]
                self.next_token = Token('T_NUM', token_string, self.line_number)
                self.current_line = self.current_line[j:]
            elif(self.current_line[i].isalpha()):
                j = i+1
                while(j < len(self.current_line) and self.current_line[j].isalnum()):
                    j += 1
                token_string = self.current_line[i:j]
                if(token_string in self.keywords):
                    self.next_token = Token(self.keyword_hash[token_string], token_string, self.line_number)
                else:
                    self.next_token = Token('T_ID', token_string, self.line_number)
                self.current_line = self.current_line[j:]
            elif(self.current_line[i] == '+'):
                self.next_token = Token('T_PLUS', "+", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '-'):
                self.next_token = Token('T_MINUS', "-", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == ';'):
                self.next_token = Token('T_SEMICOLON', ";", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == ','):
                self.next_token = Token('T_COMMA', ",", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '['):
                self.next_token = Token('T_LBRACKET', "[", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == ']'):
                self.next_token = Token('T_RBRACKET', "]", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '{'):
                self.next_token = Token('T_LBRACE', "{", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '}'):
                self.next_token = Token('T_RBRACE', "}", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '('):
                self.next_token = Token('T_LPAREN', "(", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == ')'):
                self.next_token = Token('T_RPAREN', ")", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '<'):
                j = i+1
                if(self.current_line[j] == '='):
                    self.next_token = Token('T_LEQ', "<=", self.line_number)
                    self.current_line = self.current_line[j+1:]
                else:
                    self.next_token = Token('T_LESS', "<", self.line_number)
                    self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '>'):
                j = i+1
                if(self.current_line[j] == '='):
                    self.next_token = Token('T_GEQ', ">=", self.line_number)
                    self.current_line = self.current_line[j+1:]
                else:
                    self.next_token = Token('T_GREATER', ">", self.line_number)
                    self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '='):
                j = i+1
                if(self.current_line[j] == '='):
                    self.next_token = Token('T_EQ', "==", self.line_number)
                    self.current_line = self.current_line[j+1:]
                else:
                    self.next_token = Token('T_ASSIGN', "=", self.line_number)
                    self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '!'):
                j = i+1
                if(self.current_line[j] == '='):
                    self.next_token = Token('T_NEQ', "!=", self.line_number)
                    self.current_line = self.current_line[j+1:]
                else: # TODO: exit gracefully
                    pass
            elif(self.current_line[i] == '*'):
                self.next_token = Token('T_MULT', "*", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '/'):
                j = i+1
                if(self.current_line[j] == '*'): # start of a comment block
                    j += 1
                    new_line_number = self.line_number # account for comments spanning multiple lines
                    while(self.current_line[j:j+2] != '*/'): # should not cause error if j+2 > len(self.current_line)
                        if(j == len(self.current_line)):
                            self.current_line = self.input_file.readline()
                            if not self.current_line:
                                print("ERROR: Comment block beginning at line " + str(self.line_number) + ", index " + str(i) + " is never closed.")
                                exit()
                            else:
                                new_line_number += 1
                                j = 0
                        else: # j < len(self.current_line)
                            j += 1
                    self.line_number = new_line_number
                    self.current_line = self.current_line[j+2:]
                    self.get_next_token()
                else:
                    self.next_token = Token('T_DIV', "/", self.line_number)
                    self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '%'):
                self.next_token = Token('T_MOD', "%", self.line_number)
                self.current_line = self.current_line[i+1:]
            elif(self.current_line[i] == '&'):
                self.next_token = Token('T_AND', "&", self.line_number)
                self.current_line = self.current_line[i+1:]
            else:
                print("ERROR: Unidentifiable Token at line " + str(self.line_number) + ", index " + str(i) + ".")
                exit()

def main():
    scanner = Scanner("test.bpl")
    scanner.get_next_token()
    while(scanner.next_token.kind != TokenType.T_EOF):
        print(scanner.next_token)
        scanner.get_next_token()

if __name__ == "__main__":
    main()
