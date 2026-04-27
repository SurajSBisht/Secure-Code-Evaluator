class ASTNode:
    def __init__(self, type, value=None, children=None, line=None):
        self.type = type
        self.value = value
        self.children = children if children is not None else []
        self.line = line

    def __repr__(self):
        return self._tree_repr("", True)

    def _tree_repr(self, prefix, is_last):
        res = prefix
        if prefix != "":
            res += "└── " if is_last else "├── "
            
        val_str = f": {self.value}" if self.value is not None else ""
        res += f"{self.type}{val_str}\n"
        
        child_prefix = prefix
        if prefix != "":
            child_prefix += "    " if is_last else "│   "
            
        for i, child in enumerate(self.children):
            is_last_child = (i == len(self.children) - 1)
            res += child._tree_repr(child_prefix, is_last_child)
        return res

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return ('EOF', '', getattr(self, 'last_line', -1))

    def consume(self, expected_type=None):
        token = self.current_token()
        self.last_line = token[2]

        if expected_type and token[0] != expected_type:
            raise SyntaxError(f"Line {token[2]}: Expected {expected_type}, got {token[0]} '{token[1]}'")
        
        self.pos += 1
        return token

    def parse(self):
        """
        Parses tokens to build an AST.
        Ignores outer block structures like `int main() { ... }` 
        by transparently discarding function signatures and block braces.
        """
        nodes = []
        while self.current_token()[0] != 'EOF':
            kind = self.current_token()[0]
            
            # Ignore function definitions: e.g. int main(int argc) {
            if kind == 'INT':
                # Peek forward safely to check if it matches an exact function signature
                if self.pos + 2 < len(self.tokens) and self.tokens[self.pos + 2][0] == 'LPAREN':
                    self.consume('INT')
                    self.consume('ID')
                    self.consume('LPAREN')
                    # Fast forward blindly past any arguments until RPAREN is met
                    while self.current_token()[0] not in ('RPAREN', 'EOF'):
                        self.consume()
                    self.consume('RPAREN')
                    # Consume the start of the block `{` if it exists
                    if self.current_token()[0] == 'LBRACE':
                        self.consume('LBRACE')
                    continue
            
            # Ignore extraneous closing braces (usually matched to the function blocks above)
            if kind == 'RBRACE':
                self.consume('RBRACE')
                continue
                
            # Ignore lone return statements generally found at bottom of main() functions
            if kind == 'RETURN':
                self.consume('RETURN')
                self.parse_expression()
                self.consume('SEMI')
                continue
                
            nodes.append(self.parse_statement())
            
        return ASTNode('Program', children=nodes)

    def parse_statement(self):
        token = self.current_token()
        kind = token[0]
        if kind == 'INT':
            return self.parse_var_decl()
        elif kind == 'PRINTF':
            return self.parse_print()
        elif kind == 'ID':
            return self.parse_assignment()
        else:
            raise SyntaxError(f"Line {token[2]}: Unexpected token {token[0]} '{token[1]}' starting statement")
            
    def parse_var_decl(self):
        int_tok = self.consume('INT')
        id_token = self.consume('ID')
        self.consume('ASSIGN')
        expr = self.parse_expression()
        self.consume('SEMI')
        
        return ASTNode('VarDecl', line=int_tok[2], children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[2]),
            expr
        ])

    def parse_assignment(self):
        id_token = self.consume('ID')
        self.consume('ASSIGN')
        expr = self.parse_expression()
        self.consume('SEMI')
        
        return ASTNode('Assignment', line=id_token[2], children=[
            ASTNode('Identifier', value=id_token[1], line=id_token[2]),
            expr
        ])

    def parse_print(self):
        pf_token = self.consume('PRINTF')
        
        try:
            self.consume('LPAREN')
            self.consume('STRING')
            self.consume('COMMA')
            # Extract and store only the precise identifier variable node
            id_token = self.consume('ID')
            self.consume('RPAREN')
            self.consume('SEMI')
            
            return ASTNode('PrintStmt', line=pf_token[2], children=[
                ASTNode('Identifier', value=id_token[1], line=id_token[2])
            ])
        except SyntaxError:
            # Overrule standard token errors to strictly emulate the requested C-error
            raise SyntaxError(f"Line {pf_token[2]}: Error: invalid printf syntax")

    def parse_expression(self):
        """ Parses generic addition and subtraction mapping explicitly to PLUS and MINUS AST branch nodes """
        node = self.parse_term()
        while self.current_token()[0] in ('PLUS', 'MINUS'):
            op_token = self.consume()
            right = self.parse_term()
            node = ASTNode(op_token[0], line=op_token[2], children=[node, right])
        return node

    def parse_term(self):
        """ Parses recursive mathematical multiplication and division factors into MUL and DIV AST branch nodes """
        node = self.parse_factor()
        while self.current_token()[0] in ('MUL', 'DIV'):
            op_token = self.consume()
            right = self.parse_factor()
            node = ASTNode(op_token[0], line=op_token[2], children=[node, right])
        return node

    def parse_factor(self):
        """ Resolves the base numbers, identifiers, or parentheses wrapping mathematically dense scopes """
        token = self.current_token()
        if token[0] == 'NUMBER':
            self.consume('NUMBER')
            return ASTNode('Number', value=token[1], line=token[2])
        elif token[0] == 'ID':
            self.consume('ID')
            return ASTNode('Identifier', value=token[1], line=token[2])
        elif token[0] == 'LPAREN':
            self.consume('LPAREN')
            node = self.parse_expression()
            self.consume('RPAREN')
            return node
        else:
            raise SyntaxError(f"Line {token[2]}: Expected Number, Identifier, or '('; got {token[0]} '{token[1]}'")

def parse(tokens):
    """
    Entry point to initialize the parser and run it.
    """
    p = Parser(tokens)
    return p.parse()
