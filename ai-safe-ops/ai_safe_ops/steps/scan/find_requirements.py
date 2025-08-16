import argparse
import os
import re

def find_requirements(gitingest_file: str, output_file: str):
    """
    Finds the requirements.txt file in the codebase.
    """
    with open(gitingest_file, "r") as f:
        content = f.read()

    print(f"Content of gitingest_file: {content[:500]}") # Print first 500 chars

    # Find the "Repository Structure" section
    match = re.search(r"# Repository Structure\n\n```\n(.*?)```", content, re.DOTALL)
    if not match:
        print("Repository Structure section not found.")
        return

    file_tree = match.group(1)
    print(f"File tree: {file_tree}")

    for line in file_tree.splitlines():
        if "requirements.txt" in line:
            # The line might contain indentation, so we strip it.
            path = line.strip()
            print(f"Found requirements.txt at: {path}")
            with open(output_file, "w") as f_out:
                f_out.write(path)
            return
    
    print("requirements.txt not found in file tree.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gitingest_file", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to the output file.")
    args = parser.parse_args()
    find_requirements(args.gitingest_file, args.output_file)
