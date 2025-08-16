import argparse
import json
import os
import re
import yaml
from glob import glob

# Define rules for checking config files
# This is a basic set of rules and can be expanded
CONFIG_RULES = {
    "GENERIC_SECRETS": {
        "description": "Check for generic secret keys",
        "pattern": r"secret_key|api_key|password"
    }
}

def scan_config_files(gitingest_file_path: str, output_file: str):
    """
    Scans configuration files (YAML, JSON) for common misconfigurations.
    
    Args:
        gitingest_file_path: The path to the gitingest file to identify config files.
        output_file: The file path to write the JSON results to.
    """
    if not os.path.exists(gitingest_file_path):
        raise FileNotFoundError(f"Gitingest file not found: {gitingest_file_path}")

    results = {"findings": []}
    
    codebase_path = os.path.abspath(os.path.join(os.path.dirname(gitingest_file_path), "..", ".."))

    # Find all yaml and json files in the codebase
    yaml_files = glob(os.path.join(codebase_path, "**/*.yaml"), recursive=True)
    json_files = glob(os.path.join(codebase_path, "**/*.json"), recursive=True)

    # Scan YAML files
    for file_path in yaml_files:
        with open(file_path, "r") as f:
            try:
                data = yaml.safe_load(f)
                if isinstance(data, dict):
                    for key in data.keys():
                        if re.search(CONFIG_RULES["GENERIC_SECRETS"]["pattern"], key, re.IGNORECASE):
                            results["findings"].append({
                                "type": "CONFIG_MISCONFIGURATION",
                                "file": file_path,
                                "rule": "GENERIC_SECRETS",
                                "description": CONFIG_RULES["GENERIC_SECRETS"]["description"],
                                "key": key
                            })
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {file_path}: {e}")

    # Scan JSON files
    for file_path in json_files:
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    for key in data.keys():
                        if re.search(CONFIG_RULES["GENERIC_SECRETS"]["pattern"], key, re.IGNORECASE):
                            results["findings"].append({
                                "type": "CONFIG_MISCONFIGURATION",
                                "file": file_path,
                                "rule": "GENERIC_SECRETS",
                                "description": CONFIG_RULES["GENERIC_SECRETS"]["description"],
                                "key": key
                            })
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON file {file_path}: {e}")

    with open(output_file, "w") as f:
        json.dump(results, f, indent=4)

    print(f"Config file scan completed. Results written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan config files for misconfigurations.")
    parser.add_argument("gitingest_file_path", help="The path to the gitingest file.")
    parser.add_argument("output_file", help="The path to save the JSON report.")
    args = parser.parse_args()
    scan_config_files(args.gitingest_file_path, args.output_file)
