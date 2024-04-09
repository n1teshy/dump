import os
import sys
import json


def note_to_script(src_path, dest_path):
    try:
        notebook = json.load(open(src_path))
    except json.JSONDecodeError:
        print_exit_message("Source might not be a notebook")
    cells = notebook["cells"]
    with open(dest_path, "a", encoding="utf-8") as script:
        cell_count = len(cells)
        for cell_idx, cell in enumerate(cells, start=1):
            for line_idx, line in enumerate(cell["source"], start=1):
                line_count = len(cell["source"])
                if line.startswith("!"):
                    continue
                script.write(line)
                if line_idx == line_count:
                    script.write("\n\n")
            if cell_idx < cell_count and not line.startswith("!"):
                script.write("\n")


def print_exit_message(message):
    print(f"[-] {message}")
    exit()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        message = "Invalid options\n\n"
        message += "Example:\npython /path/to/note_to_script.py /path/to/notebook.ipynb /path/to/script.py"
        print_exit_message(message)
    src, dest = sys.argv[1:3]
    src, path = os.path.abspath(src), os.path.abspath(dest)
    if not src.endswith(".ipynb"):
        print_exit_message("Source is not a notebook")
    if not os.path.exists(src):
        print_exit_message("Source does ot exist")
    if not dest.endswith(".py"):
        print_exit_message("Destination is not a python script")
    note_to_script(src, dest)
