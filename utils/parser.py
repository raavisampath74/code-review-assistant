"""
Code Parser Module
Parses uploaded source code into logical chunks for embedding generation.
"""

import ast
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CodeChunk:
    """Represents a parsed code chunk with metadata."""
    content: str
    chunk_type: str  # function, class, import, module
    name: str
    start_line: int
    end_line: int
    docstring: Optional[str] = None


class CodeParser:
    """Parses Python source code into logical chunks."""
    
    def __init__(self):
        self.chunks: List[CodeChunk] = []
    
    def parse(self, source_code: str) -> List[CodeChunk]:
        """
        Parse source code into logical chunks.
        
        Args:
            source_code: Raw Python source code
            
        Returns:
            List of CodeChunk objects
        """
        self.chunks = []
        
        try:
            tree = ast.parse(source_code)
            self._extract_chunks(tree, source_code)
        except SyntaxError as e:
            # If parsing fails, return the whole code as one chunk
            self.chunks.append(CodeChunk(
                content=source_code,
                chunk_type="module",
                name="unparseable_code",
                start_line=1,
                end_line=len(source_code.splitlines()),
                docstring=f"Syntax error: {str(e)}"
            ))
        
        return self.chunks
    
    def _extract_chunks(self, tree: ast.AST, source_code: str):
        """Extract chunks from AST."""
        lines = source_code.splitlines()
        
        # Extract imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(ast.unparse(node))
        
        if imports:
            self.chunks.append(CodeChunk(
                content="\n".join(imports),
                chunk_type="import",
                name="imports",
                start_line=1,
                end_line=len(imports)
            ))
        
        # Extract functions and classes
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.FunctionDef):
                self._add_function_chunk(node, lines)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._add_function_chunk(node, lines, is_async=True)
            elif isinstance(node, ast.ClassDef):
                self._add_class_chunk(node, lines)
    
    def _add_function_chunk(self, node: ast.FunctionDef, lines: List[str], is_async: bool = False):
        """Add a function as a chunk."""
        docstring = ast.get_docstring(node)
        content = "\n".join(lines[node.lineno - 1:node.end_lineno])
        
        self.chunks.append(CodeChunk(
            content=content,
            chunk_type="async_function" if is_async else "function",
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno,
            docstring=docstring
        ))
    
    def _add_class_chunk(self, node: ast.ClassDef, lines: List[str]):
        """Add a class as a chunk."""
        docstring = ast.get_docstring(node)
        content = "\n".join(lines[node.lineno - 1:node.end_lineno])
        
        self.chunks.append(CodeChunk(
            content=content,
            chunk_type="class",
            name=node.name,
            start_line=node.lineno,
            end_line=node.end_lineno,
            docstring=docstring
        ))
        
        # Also extract methods within the class
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_content = "\n".join(lines[item.lineno - 1:item.end_lineno])
                self.chunks.append(CodeChunk(
                    content=method_content,
                    chunk_type="method",
                    name=f"{node.name}.{item.name}",
                    start_line=item.lineno,
                    end_line=item.end_lineno,
                    docstring=ast.get_docstring(item)
                ))
    
    def get_chunk_summary(self) -> str:
        """Get a summary of parsed chunks."""
        summary = []
        for chunk in self.chunks:
            summary.append(f"[{chunk.chunk_type}] {chunk.name}: Lines {chunk.start_line}-{chunk.end_line}")
        return "\n".join(summary)


def parse_code(source_code: str) -> List[CodeChunk]:
    """
    Convenience function to parse code.
    
    Args:
        source_code: Raw Python source code
        
    Returns:
        List of CodeChunk objects
    """
    parser = CodeParser()
    return parser.parse(source_code)
