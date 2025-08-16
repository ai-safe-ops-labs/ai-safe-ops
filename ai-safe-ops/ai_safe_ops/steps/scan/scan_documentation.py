import argparse
import json
import os

def scan_documentation(codebase_path: str, output_file: str):
    """
    Checks for the existence of key documentation and legal files.

    Args:
        codebase_path: The absolute path to the codebase to scan.
        output_file: The file path to write the JSON results to.
    """
    if not os.path.isdir(codebase_path):
        raise ValueError(f"Provided codebase path is not a valid directory: {codebase_path}")

    # List of important files to check for.
    # We check for common variations (e.g., with/without extension, different cases).
    files_to_check = {
        "README": ["README.md", "README.rst", "README"],
        "LICENSE": ["LICENSE", "LICENSE.md", "LICENSE.txt"],
        "CONTRIBUTING": ["CONTRIBUTING.md", "CONTRIBUTING.rst"],
    }

    results = {"files": []}
    
    # Get all files in the root of the codebase, case-insensitively
    try:
        root_files = {f.lower(): f for f in os.listdir(codebase_path)}
    except FileNotFoundError:
        results["error"] = f"Codebase path not found: {codebase_path}"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        raise

    for key, variations in files_to_check.items():
        found_status = {
            "check_name": key,
            "found": False,
            "path": None
        }
        for variation in variations:
            if variation.lower() in root_files:
                found_status["found"] = True
                # Get the original filename with its correct case
                original_filename = root_files[variation.lower()]
                found_status["path"] = os.path.join(codebase_path, original_filename)
                break # Stop after the first match
        
        results["files"].append(found_status)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"Documentation scan completed for {codebase_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check for documentation files like README and LICENSE.")
    parser.add_argument("codebase_path", help="The path to the codebase to analyze.")
    parser.add_argument("output_file", help="The path to save the JSON report.")
    args = parser.parse_args()
    scan_documentation(args.codebase_path, args.output_file)