"""
Scan the `client/` directory for __init__.py files.
For every depth-1 import, add it, in order, to the __all__ variable.
"""
import ast
import os
import re
from pathlib import Path
from typing import List


class ImportVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.imported_names: List[str] = []

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.level == 1:
            for name in node.names:
                self.imported_names.append(name.asname or name.name)


def main() -> None:
    impl_root = Path.cwd() / "client/src/telethon/_impl"
    autogenerated_re = re.compile(
        rf"(tl|mtproto){re.escape(os.path.sep)}(abcs|functions|types)"
    )

    files = []
    for file in impl_root.rglob("__init__.py"):
        file_str = str(file)
        if autogenerated_re.search(file_str):
            continue

        files.append(file_str)

        with file.open(encoding="utf-8") as fd:
            contents = fd.read()
        lines = contents.splitlines(True)

        module = ast.parse(contents)

        visitor = ImportVisitor()
        visitor.visit(module)

        for stmt in module.body:
            match stmt:
                case ast.Assign(targets=[ast.Name(id="__all__")], value=ast.List()):
                    # Not rewriting the AST to preserve comments and formatting.
                    lines[stmt.lineno - 1 : stmt.end_lineno] = [
                        "__all__ = ["
                        + ", ".join(map(repr, visitor.imported_names))
                        + "]\n"
                    ]
                    break

        with file.open("w", encoding="utf-8", newline="\n") as fd:
            fd.writelines(lines)


if __name__ == "__main__":
    main()
