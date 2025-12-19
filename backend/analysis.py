import ast
import os
from typing import List, Dict

def walk_repo_and_parse(root_path: str) -> List[Dict]:
    """
    Walk the repo, parse Python files, and extract modules/classes/functions.
    Returns a list of symbol dicts.
    """
    symbols = []
    for dirpath, _, filenames in os.walk(root_path):
        if any(excluded in dirpath for excluded in ["venv", "node_modules", ".git"]):
            continue
        for filename in filenames:
            if filename.endswith(".py"):
                file_path = os.path.join(dirpath, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    try:
                        tree = ast.parse(f.read(), filename=filename)
                        symbols.extend(extract_symbols(tree, file_path))
                    except Exception as e:
                        print(f"Error parsing {file_path}: {e}")
    return symbols

def extract_symbols(tree: ast.AST, file_path: str) -> List[Dict]:
    """
    Extract classes and functions from AST.
    """
    symbols = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            symbols.append({
                "type": "class",
                "name": node.name,
                "file": file_path,
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node)
            })
        elif isinstance(node, ast.FunctionDef):
            symbols.append({
                "type": "function",
                "name": node.name,
                "file": file_path,
                "lineno": node.lineno,
                "docstring": ast.get_docstring(node)
            })
    return symbols
