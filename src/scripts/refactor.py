import os
import ast
from pathlib import Path

def refactor_prompt_templates(folder):
    """
    Recursively scans the given folder for .py files. If a file contains a top-level
    assignment to PROMPT_TEMPLATE (a string literal), it extracts that string, removes
    the assignment, and inserts an import statement so that PROMPT_TEMPLATE is set from
    the TEMPLATES dict (defined in folder/templates.py). The templates are stored in a dict
    mapping the file's relative path (POSIX style) to the template string.
    """
    templates = {}  # This will hold mapping: relative_file_path -> template string
    folder = os.path.abspath(folder)

    # Walk through all .py files recursively
    for dirpath, _, files in os.walk(folder):
        for file in files:
            if not file.endswith(".py"):
                continue
            print(f"Processing {file}")
            full_path = os.path.join(dirpath, file)
            # Skip the templates file itself if present
            if os.path.abspath(full_path) == os.path.join(folder, "templates.py"):
                continue

            with open(full_path, "r", encoding="utf-8") as f:
                source = f.read()

            try:
                tree = ast.parse(source, filename=full_path)
            except SyntaxError:
                print(f"Syntax error in {full_path}; skipping.")
                continue

            # Look for a top-level assignment to PROMPT_TEMPLATE
            prompt_node = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "PROBLEM_TEMPLATE":
                            # We only support string literal assignments.
                            if (isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
                                prompt_node = node
                                break
                    if prompt_node:
                        break

            # If not found, nothing to do in this file.
            if not prompt_node:
                continue
            print(f"Found PROBLEM_TEMPLATE in {full_path}")
            # Extract the template string.
            if isinstance(prompt_node.value, ast.Constant):
                template_str = prompt_node.value.value
            else:  # fallback for older Python versions (ast.Str)
                template_str = prompt_node.value.s

            # Compute the file’s relative path (in POSIX style) to be used as a key.
            rel_path = Path(full_path).relative_to(folder).as_posix()
            templates[rel_path] = template_str

            # Remove the PROBLEM_TEMPLATE assignment from the file.
            # We rely on the node’s lineno and end_lineno (both 1-indexed).
            lines = source.splitlines()
            # Remove the lines corresponding to the assignment.
            del lines[prompt_node.lineno - 1 : prompt_node.end_lineno]

            # Determine where to insert the new import statements.
            # We'll try to keep any shebang, encoding, or module docstring at the top.
            insertion_index = 0
            # If the first line is a shebang, skip it.
            if lines and lines[0].startswith("#!"):
                insertion_index = 1
            # If the next line looks like an encoding declaration, skip that too.
            if len(lines) > insertion_index and "coding" in lines[insertion_index]:
                insertion_index += 1
            # Check for a module docstring (if the first statement is a string literal).
            # Note: We use the original AST to get the docstring node's end line.
            if tree.body and isinstance(tree.body[0], ast.Expr) and \
               isinstance(tree.body[0].value, (ast.Str, ast.Constant)):
                # The docstring node's end_lineno tells us where it ends.
                insertion_index = max(insertion_index, tree.body[0].end_lineno)

            # Prepare the two lines to insert.
            import_lines = [
                "from math_construct.problems.templates import TEMPLATES",
                f'PROBLEM_TEMPLATE = TEMPLATES["{rel_path}"]',
                ""  # extra blank line for readability
            ]
            # Insert the new lines.
            new_lines = lines[:insertion_index] + import_lines + lines[insertion_index:]
            new_source = "\n".join(new_lines) + "\n"

            # Write the modified source back to the file.
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(new_source)
            print(f"Processed {rel_path}")

    # Now write the templates.py file in the given folder.
    templates_path = os.path.join(folder, "templates.py")
    with open(templates_path, "w", encoding="utf-8") as f:
        f.write("TEMPLATES = {\n")
        for key, template in templates.items():
            # Use repr to safely represent the strings.
            f.write(f"    {repr(key)}: {repr(template)},\n")
        f.write("}\n")
    print(f"Created {templates_path}")

# Example usage:
# refactor_prompt_templates("folder")
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Refactor prompt templates in Python files.")
    parser.add_argument("--folder", default="src/math_construct/problems", type=str)

    args = parser.parse_args()
    refactor_prompt_templates(args.folder)