"""FULL_CONTEXT control arm (P0-3): the whole subject repository, no retrieval.

Supplies the source of every non-test file in the subject in place of the k
retrieved chunks, so the only thing that differs from the RAG arm is where
the context comes from. Same prompt template and wrapper, same one-retry
loop, same validator, same temperature.

Author decision (2026-10-01): "excluding the mutant itself" means excluding
only the FUNCTION UNDER TEST (it is already shown in the prompt), not its
whole file; the rest of that file stays. This mirrors the RAG retriever,
which drops the function-under-test chunk and keeps its siblings.
"Test files" use the repo-wide rule from core.srcmap (a file is a test file
if "test" appears in its file name). The pinned subject is read, never the
mutated scratch copy.
"""
from __future__ import annotations

import ast
from pathlib import Path

from core.srcmap import iter_python_files

OMITTED = "# <function under test omitted: it is given separately in the prompt>"


def _omit_function(src: str, qualname: str) -> str:
    """Replace the source lines of function `qualname` with a one-line marker."""
    tree = ast.parse(src)
    found: list[ast.AST] = []

    def walk(node, stack):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if ".".join(stack + [child.name]) == qualname:
                    found.append(child)
                walk(child, stack + [child.name])
            elif isinstance(child, ast.ClassDef):
                walk(child, stack + [child.name])
            else:
                walk(child, stack)
    walk(tree, [])
    if not found:
        return src
    node = found[0]
    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
    lines = src.splitlines()
    indent = lines[start - 1][:len(lines[start - 1]) - len(lines[start - 1].lstrip())]
    return "\n".join(lines[:start - 1] + [indent + OMITTED]
                     + lines[node.end_lineno:])


def build_full_context(repo_root: Path, subdir: str, mutant: dict) -> list[dict]:
    """One chunk per non-test source file, in path order, in the same chunk
    shape the RAG arm hands to llm_rewriter.format_context_section."""
    chunks = []
    for path in iter_python_files(Path(repo_root), subdir):
        rel = path.relative_to(repo_root).as_posix()
        if "test" in path.name:
            continue
        try:
            src = path.read_text(encoding="utf-8")
            ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        if rel == mutant["file"]:
            src = _omit_function(src, mutant["function"])
        chunks.append({"id": f"{rel}::full_file", "document": src,
                       "metadata": {"file": rel, "qualname": "(entire file)",
                                    "kind": "full_file"},
                       "distance": 0.0})
    return chunks
