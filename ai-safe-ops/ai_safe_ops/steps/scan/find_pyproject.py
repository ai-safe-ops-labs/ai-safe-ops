import argparse
import os
import re

def find_pyproject(codebase_path: str, gitingest_file_path: str, output_file: str):
    """
    Finds the pyproject.toml file in the codebase.
    """
    with open(gitingest_file_path, "r") as f:
        content = f.read()

    # Find the "Repository Structure" section
    match = re.search(r"# Repository Structure\n\n```\n(.*?)```", content, re.DOTALL)
    if not match:
        return

    file_tree = match.group(1)
    for line in file_tree.splitlines():
        if "pyproject.toml" in line:
            # The line might contain indentation, so we strip it.
            path = line.strip()
            
            # Construct the absolute path.
            abs_path = os.path.join(codebase_path, path)
            
            with open(output_file, "w") as f_out:
                f_out.write(abs_path)
            return

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("codebase_path", help="The path to the codebase.")
    parser.add_argument("gitingest_file_path", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to the output file.")
    args = parser.parse_args()
    find_pyproject(args.codebase_path, args.gitingest_file_path, args.output_file)
