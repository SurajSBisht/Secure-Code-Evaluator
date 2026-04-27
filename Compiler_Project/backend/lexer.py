import re

def lex(code):
    """
    Complete lexical analyzer for a subset of the C language.
    Takes a source code string and returns a list of tuples (TYPE, VALUE, LINE).
    """
    # Define token specifications
    token_specification = [
        # Comments (Single-line '//' and Multi-line '/* ... */')
        ('COMMENT',  r'//[^\n]*|/\*[\s\S]*?\*/'),
        
        # String Literals
        ('STRING',   r'"[^"]*"'),
        
        # Keywords
        ('INT',      r'\bint\b'),
        ('PRINTF',   r'\bprintf\b'),
        ('IF',       r'\bif\b'),
        ('ELSE',     r'\belse\b'),
        ('WHILE',    r'\bwhile\b'),
        ('RETURN',   r'\breturn\b'),
        
        # Identifiers
        ('ID',       r'[A-Za-z_][A-Za-z0-9_]*'),
        
        # Numbers (Integers)
        ('NUMBER',   r'\d+'),
        
        # Multi-character Operators
        ('EQ',       r'=='),
        ('NEQ',      r'!='),
        
        # Single-character Operators
        ('ASSIGN',   r'='),
        ('LT',       r'<'),
        ('GT',       r'>'),
        ('PLUS',     r'\+'),
        ('MINUS',    r'-'),
        ('MUL',      r'\*'),
        ('DIV',      r'/'),
        
        # Delimiters
        ('SEMI',     r';'),
        ('COMMA',    r','),
        ('LPAREN',   r'\('),
        ('RPAREN',   r'\)'),
        ('LBRACE',   r'\{'),
        ('RBRACE',   r'\}'),
        
        # Newline (for line tracking)
        ('NEWLINE',  r'\n'),
        
        # Whitespace
        ('SKIP',     r'[ \t\r]+'),
        
        # Any other character (Mismatch/Error)
        ('MISMATCH', r'.'),
    ]

    # Combine into a single compiled regular expression
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    
    tokens = []
    line_num = 1
    
    # Iterate over all matches
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group(kind)
        
        if kind == 'NEWLINE':
            line_num += 1
            continue
        elif kind == 'COMMENT':
            # Count the new lines dynamically out of multiline-block comments
            line_num += value.count('\n')
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Unexpected character {value!r} at line {line_num}')
        else:
            tokens.append((kind, value, line_num))
            
    return tokens

def format_tokens(tokens):
    """Utility function to provide a clean structured output of the tokens"""
    output = []
    output.append(f"{'TYPE':<12} | {'VALUE':<10} | {'LINE'}")
    output.append("-" * 35)
    for token_type, token_value, line in tokens:
        output.append(f"{token_type:<12} | {token_value:<10} | {line}")
    return '\n'.join(output)

if __name__ == '__main__':
    # A simple test for the analyzer
    sample_code = '''
    // Variable declaration
    int x = 10;
    
    /* 
       Loop block test 
    */
    while (x < 20) {
        printf(x);
        x = x + 1;
        
        if (x == 15) {
            return 0;
        }
    }
    '''
    tokens = lex(sample_code)
    print(format_tokens(tokens))
