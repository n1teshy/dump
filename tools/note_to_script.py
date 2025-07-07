import os
import sys
import json
import argparse
import subprocess
import platform
import re

REQUIRED_LIBRARIES = {
    "pygments": "pygments"
}


def check_dependencies():
    missing = []
    for module, package in REQUIRED_LIBRARIES.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(package)

    if missing:
        print("[-] Missing required libraries:")
        for lib in missing:
            print(f"   - {lib}")
        print("\n[+] You can install them using:")
        print(f"   pip install {' '.join(missing)}\n")
        sys.exit(1)


def parse_block_indices(block_arg, total_cells):
    indices = []
    if block_arg:
        block_arg = block_arg.strip()
        if ":" in block_arg:
            try:
                start, end = [arg.strip() for arg in block_arg.split(":")]
                start = max(int(start or 0), 0)
                end = min(int(end or total_cells), total_cells)
                if start >= end or start < 0:
                    print_exit_message("Invalid range in --blocks")
                indices = list(range(start, end))
            except ValueError:
                print_exit_message("Invalid format for --blocks")
        else:
            try:
                indices = [int(i.strip()) for i in block_arg.split(",") if i.strip().isdigit()]
                indices = [i for i in indices if i < total_cells]
            except ValueError:
                print_exit_message("Invalid format for --blocks")
    return indices


def note_to_script(src_path, dest_path=None, clip=False, block_arg=None):
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import TerminalFormatter

    try:
        with open(src_path, encoding="utf-8") as f:
            notebook = json.load(f)
        cells = notebook["cells"]
    except (json.JSONDecodeError, KeyError):
        print_exit_message("Source might not be a valid notebook")

    total_cells = len(cells)
    selected_indices = parse_block_indices(block_arg, total_cells)
    selected_cells = [cells[i] for i in selected_indices if cells[i].get("cell_type") == "code"] if selected_indices else [cell for cell in cells if cell.get("cell_type") == "code"]


    code_lines = []
    cell_count = len(selected_cells)
    for cell_idx, cell in enumerate(selected_cells, start=1):
        for line_idx, line in enumerate(cell.get("source", []), start=1):
            line_count = len(cell["source"])
            if line.startswith("!"):
                line = f"# {line.strip('! ')}"
            code_lines.append(line)
            if line_idx == line_count:
                code_lines.append("\n\n")
        if cell_idx < cell_count and not line.startswith("!"):
            code_lines.append("\n")

    code = "".join(code_lines)

    if clip:
        copy_to_clipboard(code)
    elif dest_path:
        with open(dest_path, "a", encoding="utf-8") as script:
            script.write(code)
    else:
        print(highlight(code, PythonLexer(), TerminalFormatter()))


def copy_to_clipboard(text):
    if platform.system() == "Windows":
        try:
            subprocess.run("clip", text=True, input=text, check=True)
            print("[+] Code copied to clipboard.")
        except subprocess.CalledProcessError:
            print("[-] Failed to copy to clipboard.")
    else:
        print("[-] Clipboard copy is only supported on Windows in this script.")


def print_exit_message(message):
    print(f"[-] {message}")
    sys.exit(1)


def main():
    check_dependencies()

    parser = argparse.ArgumentParser(
        description="Convert Jupyter Notebook (.ipynb) to Python script (.py)"
    )
    parser.add_argument("notebook_file", help="Path to the source notebook file (.ipynb)")
    parser.add_argument(
        "python_file", nargs="?", default=None, help="Path to the destination Python script (.py)"
    )
    parser.add_argument(
        "--clip", action="store_true", help="Copy the converted code to clipboard (Windows only)"
    )
    parser.add_argument(
        "--blocks",
        type=str,
        help="Comma-separated list of cell indices (e.g. 0,2,5) or a range (e.g. 2:6)"
    )
    args = parser.parse_args(sys.argv[1:] or ["--help"])

    notebook_file = os.path.abspath(args.notebook_file)
    python_file = os.path.abspath(args.python_file) if args.python_file else None

    if not notebook_file.endswith(".ipynb"):
        print_exit_message("Source is not a notebook")
    if not os.path.exists(notebook_file):
        print_exit_message("Source does not exist")

    note_to_script(notebook_file, python_file, args.clip, args.blocks)


if __name__ == "__main__":
    main()
