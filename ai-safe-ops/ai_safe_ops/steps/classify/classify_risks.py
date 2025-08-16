import argparse
import json
import os

# A simple risk classification mapping.
# This can be expanded with more sophisticated rules.
RISK_CLASSIFICATION = {
    "PII_EXPOSURE": "High",
    "CONFIG_MISCONFIGURATION": "Medium",
    "POTENTIAL_BIAS": "Low",
    "DEFAULT": "Info"
}

def classify_risks(analysis_files: list, output_file: str):
    """
    Classifies the findings from various analysis steps into risk categories.
    
    Args:
        analysis_files: A list of paths to the JSON output files from analysis steps.
        output_file: The file path to write the classified results to.
    """
    classified_results = {"findings": []}

    for file_path in analysis_files:
        if not os.path.exists(file_path):
            print(f"Warning: Analysis file not found, skipping: {file_path}")
            continue
        
        with open(file_path, "r") as f:
            try:
                data = json.load(f)
                for finding in data.get("findings", []):
                    finding_type = finding.get("type", "")
                    risk_level = RISK_CLASSIFICATION.get(finding_type, RISK_CLASSIFICATION["DEFAULT"])
                    finding["risk_level"] = risk_level
                    classified_results["findings"].append(finding)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from {file_path}: {e}")

    with open(output_file, "w") as f:
        json.dump(classified_results, f, indent=4)

    print(f"Risk classification completed. Results written to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Classify risks from analysis findings.")
    parser.add_argument("output_file", help="The path to save the classified JSON report.")
    parser.add_argument("analysis_files", nargs='+', help="The paths to the analysis JSON files.")
    args = parser.parse_args()
    classify_risks(args.analysis_files, args.output_file)
