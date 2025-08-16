import argparse
import json
import os
import re
import spacy
import sys
import subprocess

# A simple list of potentially biased terms.
# This should be expanded and refined based on research.
BIAS_TERMS = [
    "master", "slave", "blacklist", "whitelist", "guys", "man-hours"
]

def download_spacy_model(model_name="en_core_web_sm"):
    """Downloads the spaCy model if it's not already installed."""
    try:
        spacy.load(model_name)
    except OSError:
        print(f"Downloading spaCy model: {model_name}")
        subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])

def check_bias_heuristics(gitingest_file_path: str, output_file: str):
    """
    Scans codebase comments and variable names for potentially biased language.
    
    Args:
        gitingest_file_path: The path to the gitingest file containing the codebase content.
        output_file: The file path to write the JSON results to.
    """
    download_spacy_model()
    nlp = spacy.load("en_core_web_sm")

    if not os.path.exists(gitingest_file_path):
        raise FileNotFoundError(f"Gitingest file not found: {gitingest_file_path}")

    results = {"findings": []}
    
    with open(gitingest_file_path, "r") as f:
        content = f.read()

    # Simple regex to extract comments and variable names (can be improved)
    # For now, we just scan the whole text
    doc = nlp(content)
    
    for token in doc:
        if token.text.lower() in BIAS_TERMS:
            line_number = content.count('\n', 0, token.idx) + 1
            finding = {
                "type": "POTENTIAL_BIAS",
                "term": token.text,
                "line": line_number,
                "description": "Found potentially biased language."
            }
            results["findings"].append(finding)

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Bias heuristics scan completed. Results written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for biased language in code.")
    parser.add_argument("gitingest_file_path", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to save the JSON report.")
    args = parser.parse_args()
    check_bias_heuristics(args.gitingest_file_path, args.output_file)
