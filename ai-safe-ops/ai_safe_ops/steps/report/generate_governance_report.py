import argparse
import json
import os

def generate_governance_report(classified_risks_file: str, output_file: str, log_dir: str, executed_steps: list[str]):
    """
    Generates a markdown report from the classified risk findings.
    
    Args:
        classified_risks_file: The path to the JSON file with classified risks.
        output_file: The file path to write the markdown report to.
        log_dir: The directory where the logs are stored.
        executed_steps: A list of names of the steps that were executed.
    """
    report_parts = []
    recommendations = []
    
    report_parts.append("# AI Safe Ops 360 - Governance Report")
    report_parts.append("---")

    try:
        with open(classified_risks_file) as f:
            data = json.load(f)
        
        findings = data.get("findings", [])
        
        # Group findings by step type
        findings_by_step = {}
        for finding in findings:
            step_type = finding.get("type")
            if step_type not in findings_by_step:
                findings_by_step[step_type] = []
            findings_by_step[step_type].append(finding)

        # Filter out reporting and classification steps from the executed_steps list
        steps_to_report = [step for step in executed_steps if step not in ["ingest_codebase", "classify_risks", "generate_governance_report"]]

        report_parts.append("\n## Scan Results")
        for step_name in steps_to_report:
            report_parts.append(f"\n### 🛡️ **{step_name.replace('_', ' ').title()}**")
            if step_name in findings_by_step:
                # Sort findings by risk level
                sorted_findings = sorted(findings_by_step[step_name], key=lambda x: ["High", "Medium", "Low", "Info"].index(x.get("risk_level", "Info")))
                for finding in sorted_findings:
                    risk_level = finding.get("risk_level", "Info")
                    report_parts.append(f"*   **[{risk_level}]** {finding.get('description', '')}")
                    if 'file' in finding:
                        report_parts.append(f"    *   **File:** {finding.get('file')}")
                    if 'line' in finding:
                        report_parts.append(f"    *   **Line:** {finding.get('line')}")
                    if 'term' in finding:
                        report_parts.append(f"    *   **Term:** {finding.get('term')}")
                    if 'key' in finding:
                        report_parts.append(f"    *   **Key:** {finding.get('key')}")
            else:
                report_parts.append("*   ✅ No issues found.")


    except (IOError, json.JSONDecodeError) as e:
        report_parts.append(f"Error generating report: {e}")

    # --- Recommendations Section ---
    if recommendations:
        report_parts.append("\n## 🚀 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            report_parts.append(f"{i}.  **{rec}**")

    # --- Log File Path ---
    report_parts.append("\n---\n")
    report_parts.append(f"👉 *For full details, see the log files in:\n{log_dir}")

    # --- Write final report ---
    with open(output_file, "w") as f:
        f.write("\n".join(report_parts))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a governance report from classified risks.")
    parser.add_argument("classified_risks_file", help="The path to the classified risks JSON file.")
    parser.add_argument("output_file", help="The path to save the markdown report.")
    parser.add_argument("log_dir", help="The path to the log directory.")
    parser.add_argument('executed_steps', nargs='+', help='A list of executed step names.')
    args = parser.parse_args()
    generate_governance_report(args.classified_risks_file, args.output_file, args.log_dir, args.executed_steps)