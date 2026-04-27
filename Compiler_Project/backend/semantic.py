class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = {}
        self.errors = []

    def analyze(self, ast_root):
        """
        Traverses the AST starting from the root to perform semantic checks.
        Returns a list of semantic error strings.
        """
        self.errors = []
        self.symbol_table = {}
        self.visit(ast_root)
        return self.errors

    def visit(self, node):
        """
        Recursively visits AST nodes, performs checks, and returns the evaluated type.
        """
        if node is None:
            return None

        # Fallback to an empty mark if the parser generated a node missing specific positional mapping
        line = getattr(node, 'line', '?')

        if node.type == 'Program':
            for child in node.children:
                self.visit(child)
                
        elif node.type == 'VarDecl':
            id_node = node.children[0]
            var_name = id_node.value
            var_line = getattr(id_node, 'line', line)
            
            # In variable declarations, we evaluate the expression on the right first theoretically
            self.visit(node.children[1])
            
            if var_name in self.symbol_table:
                self.errors.append(f"Line {var_line}: Error: redefinition of '{var_name}'")
            else:
                self.symbol_table[var_name] = 'int'
                
        elif node.type == 'Assignment':
            id_node = node.children[0]
            var_name = id_node.value
            var_line = getattr(id_node, 'line', line)
            
            # The right hand side is evaluated first
            self.visit(node.children[1])
            
            if var_name not in self.symbol_table:
                self.errors.append(f"Line {var_line}: Error: '{var_name}' undeclared (first use in this function)")
                # Add to symbol table so we don't spam the console continuously for the same unmapped variable
                self.symbol_table[var_name] = 'int'
                    
        elif node.type == 'PrintStmt':
            self.visit(node.children[0])
            
        elif node.type in ('PLUS', 'MINUS', 'MUL', 'DIV'):
            self.visit(node.children[0])
            self.visit(node.children[1])
            return 'int'
            
        elif node.type == 'Identifier':
            var_name = node.value
            if var_name not in self.symbol_table:
                self.errors.append(f"Line {line}: Error: '{var_name}' undeclared (first use in this function)")
                self.symbol_table[var_name] = 'int'
            return 'int'
            
        elif node.type == 'Number':
            return 'int'
        
        return None

def analyze(ast_root):
    """
    Entry point to initialize the semantic analyzer and run it.
    """
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast_root)
