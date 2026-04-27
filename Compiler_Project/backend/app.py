from flask import Flask, request, jsonify
from flask_cors import CORS
import re

from lexer import lex
from parser import parse
from semantic import analyze

app = Flask(__name__)
# Enable CORS for all routes so frontend interfaces on different ports can ping it
CORS(app)

def preprocess_code(code):
    """
    Sanitizes raw C boilerplates into the lean analysis subset.
    - Validates #include lines against an allowed list
    - Removes #include lines after successful validation
    - Removes 'int main() {' wrappers
    - Removes 'return 0;' 
    - Sanitizes 'printf("%d", a);' formatted calls into 'printf(a);'
    """
    allowed_headers = {'stdio.h', 'stdlib.h', 'math.h'}
    
    # Extract and evaluate all included headers
    for match in re.finditer(r'#include\s*[<"]([^>"]+)[>"]', code):
        header = match.group(1)
        if header not in allowed_headers:
            raise ValueError(f"invalid header file '{header}'")
            
    # Remove validated includes so the main AST parser evaluates smoothly
    code = re.sub(r'#include\s*[<"][^>"]+[>"]\s*\n?', '', code)
    
    # Remove standard main wrappers
    code = re.sub(r'int\s+main\s*\([^)]*\)\s*\{', '', code)
    code = re.sub(r'return\s+0\s*;', '', code)
    

    
    return code

def serialize_ast(node):
    """
    Recursively converts ASTNode objects into standard python dictionaries
    so that they can be easily serialized into JSON.
    """
    if node is None:
        return None
    return {
        "type": node.type,
        "value": node.value,
        "children": [serialize_ast(child) for child in node.children]
    }

@app.route('/', methods=['GET'])
def index():
    """
    Root route to verify the API server is available.
    """
    return "C Compiler Backend Running"

@app.route('/analyze', methods=['POST'])
def analyze_code():
    data = request.get_json()
    if not data or 'code' not in data:
        return jsonify({"error": "Missing 'code' string in JSON body"}), 400
        
    code = data['code']
    
    # 0. Preprocess
    try:
        code = preprocess_code(code)
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 400
    
    # 1. Lexical Analysis
    try:
        tokens = lex(code)
    except Exception as e:
        return jsonify({"error": f"Lexer Error: {str(e)}"}), 400
        
    # Clean up tokens into a list of dicts for the frontend
    serialized_tokens = [{"type": t[0], "value": t[1], "line": t[2]} for t in tokens]
        
    # 2. Syntax Analysis (Parsing)
    try:
        ast_root = parse(tokens)
        serialized_ast = serialize_ast(ast_root)
    except Exception as e:
        return jsonify({
            "tokens": serialized_tokens,
            "error": f"Parser Error: {str(e)}"
        }), 400
        
    # 3. Semantic Analysis
    try:
        semantic_errors = analyze(ast_root)
    except Exception as e:
         return jsonify({
            "tokens": serialized_tokens,
            "ast": serialized_ast,
            "error": f"Semantic Interface Error: {str(e)}"
        }), 400
        
    # Return Unified JSON Output
    return jsonify({
        "tokens": serialized_tokens,
        "ast": serialized_ast,
        "errors": semantic_errors
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
