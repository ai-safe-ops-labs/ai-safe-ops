import argparse
import json

def scan_tech_stack(gitingest_file_path: str, output_file: str):
    """
    Scans the gitingest file to identify the tech stack.
    """
    with open(gitingest_file_path, "r") as f:
        content = f.read()

    tech_stack = {}

    if "python" in content.lower():
        tech_stack["python"] = "detected"
    if "go" in content.lower():
        tech_stack["go"] = "detected"
    if "javascript" in content.lower():
        tech_stack["javascript"] = "detected"
    if "typescript" in content.lower():
        tech_stack["typescript"] = "detected"
    if "java" in content.lower():
        tech_stack["java"] = "detected"
    if "ruby" in content.lower():
        tech_stack["ruby"] = "detected"
    if "php" in content.lower():
        tech_stack["php"] = "detected"
    if "c#" in content.lower():
        tech_stack["c#"] = "detected"
    if "c++" in content.lower():
        tech_stack["c++"] = "detected"
    if "c" in content.lower():
        tech_stack["c"] = "detected"
    if "swift" in content.lower():
        tech_stack["swift"] = "detected"
    if "kotlin" in content.lower():
        tech_stack["kotlin"] = "detected"
    if "scala" in content.lower():
        tech_stack["scala"] = "detected"
    if "rust" in content.lower():
        tech_stack["rust"] = "detected"
    if "dart" in content.lower():
        tech_stack["dart"] = "detected"

    with open(output_file, "w") as f:
        json.dump(tech_stack, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gitingest_file_path", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to the output file.")
    args = parser.parse_args()
    scan_tech_stack(args.gitingest_file_path, args.output_file)
