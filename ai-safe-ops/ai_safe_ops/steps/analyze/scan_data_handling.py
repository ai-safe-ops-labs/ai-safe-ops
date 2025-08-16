import argparse
import json
import os
import re
import sys

# Basic PII regex patterns
# This is not an exhaustive list and should be expanded
PII_PATTERNS = {
    "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
    "PHONE_NUMBER": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
    "CREDIT_CARD": r"\b(?:\d{4}[- ]?){3}\d{4}\b",
    "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
}

def scan_data_handling(gitingest_file_path: str, output_file: str):
    """
    Scans the codebase for potential PII and sensitive data handling issues.
    
    Args:
        gitingest_file_path: The path to the gitingest file containing the codebase content.
        output_file: The file path to write the JSON results to.
    """
    if not os.path.exists(gitingest_file_path):
        raise FileNotFoundError(f"Gitingest file not found: {gitingest_file_path}")

    results = {"findings": []}
    
    with open(gitingest_file_path, "r") as f:
        content = f.read()

    for pii_type, pattern in PII_PATTERNS.items():
        for match in re.finditer(pattern, content):
            line_number = content.count('\n', 0, match.start()) + 1
            finding = {
                "type": "PII_EXPOSURE",
                "pii_type": pii_type,
                "value": match.group(0),
                "line": line_number
            }
            results["findings"].append(finding)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Data handling scan completed. Results written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for sensitive data handling issues.")
    parser.add_argument("gitingest_file_path", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to save the JSON report.")
    args = parser.parse_args()
    scan_data_handling(args.gitingest_file_path, args.output_file)
