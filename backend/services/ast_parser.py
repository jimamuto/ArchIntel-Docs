
import ast
import re
from typing import Dict, List, Any

def parse_code_structure(content: str, language: str) -> Dict[str, Any]:
    """
    Parses code content to extract structural information (classes, functions, imports).
    Returns a dictionary suitable for LLM context to understand system architecture
    without reading every line of code.
    """
    if language.lower() == 'python':
        return parse_python(content)
    elif language.lower() in ['javascript', 'typescript', 'js', 'ts', 'jsx', 'tsx']:
        return parse_javascript(content)
    else:
        return {"summary": "Structure parsing not supported for this language", "size": len(content)}

def parse_python(content: str) -> Dict[str, Any]:
    try:
        tree = ast.parse(content)
        structure = {
            "imports": [],
            "classes": [],
            "functions": [],
            "constants": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    structure["imports"].append(name.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for name in node.names:
                    structure["imports"].append(f"{module}.{name.name}")
            elif isinstance(node, ast.ClassDef):
                methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                structure["classes"].append({
                    "name": node.name,
                    "methods": methods,
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.FunctionDef):
                # Only top-level functions or those not caught by ClassDef walk if we adjusted traversal
                if isinstance(node.parent, ast.Module) if hasattr(node, 'parent') else True: 
                    # Note: ast.walk doesn't set parent. 
                    # But for simple summary, listing all functions is fine, mostly interested in naming.
                    pass
                    
        # Re-walk for top level functions only to avoid duplicates from classes
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                structure["functions"].append({
                    "name": node.name,
                    "args": [a.arg for a in node.args.args],
                    "docstring": ast.get_docstring(node)
                })
            elif isinstance(node, ast.Assign):
                # Heuristic for constants
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id.isupper():
                        structure["constants"].append(target.id)
                        
        return structure
    except Exception as e:
        return {"error": f"Failed to parse Python structure: {str(e)}"}

def parse_javascript(content: str) -> Dict[str, Any]:
    """
    Regex-based parsing for JS/TS since we don't have a JS AST parser in Python stdlib.
    """
    structure = {
        "imports": [],
        "classes": [],
        "functions": [],
        "exports": []
    }
    
    # Simple regexes for standard patterns
    import_pattern = re.compile(r'import\s+.*?\s+from\s+[\'"](.*?)[\'"];?')
    class_pattern = re.compile(r'class\s+(\w+)')
    function_pattern = re.compile(r'function\s+(\w+)\s*\(')
    const_func_pattern = re.compile(r'const\s+(\w+)\s*=\s*(\(.*\)|async\s*\(.*\))\s*=>')
    export_pattern = re.compile(r'export\s+(default\s+)?(class|function|const)\s+(\w+)')
    
    structure["imports"] = import_pattern.findall(content)
    structure["classes"] = [{"name": m} for m in class_pattern.findall(content)]
    
    funcs = function_pattern.findall(content)
    arrow_funcs = const_func_pattern.findall(content)
    structure["functions"] = [{"name": f} for f in funcs] + [{"name": f[0]} for f in arrow_funcs]
    
    exports = export_pattern.findall(content)
    structure["exports"] = [e[2] for e in exports]
    
    return structure
