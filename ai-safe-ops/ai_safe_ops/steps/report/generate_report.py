import argparse
import json
import os
import re

def parse_secret_type(secret_string):
    """Extracts the 'Secret Type' from the detect-secrets output string."""
    match = re.search(r"Secret Type: (.*)", secret_string)
    if match:
        return match.group(1)
    return "Unknown Type"

def generate_report(
    documentation_file: str,
    secrets_file: str,
    dependencies_file: str,
    static_code_analysis_file: str,
    output_file: str,
    log_dir: str
):
    """
    Aggregates results from all scans and generates a detailed markdown report.
    """
    report_parts = []
    recommendations = []
    
    report_parts.append("# AI Safe Ops 360 - Executive Summary")
    report_parts.append("---")

    # --- Documentation Section ---
    report_parts.append("## 📝 Documentation & Transparency")
    try:
        with open(documentation_file) as f:
            doc_data = json.load(f)
        for file_check in doc_data.get("files", []):
            status = "✅ Found" if file_check["found"] else "❌ NOT FOUND"
            report_parts.append(f"*   **{file_check['check_name']} File:** {status}")
            if not file_check["found"] and file_check['check_name'] != "README":
                 recommendations.append(f"Add a `{file_check['check_name']}` file to your repository root.")
    except (IOError, json.JSONDecodeError):
        report_parts.append("*   Could not analyze documentation files.")

    # --- Security Section ---
    report_parts.append("\n## 🛡️ Security")
    
    # Secrets
    try:
        with open(secrets_file) as f:
            secrets_data = json.load(f)
        
        all_secrets = [item for sublist in secrets_data.values() for item in sublist]
        num_secrets = len(all_secrets)
        
        if num_secrets > 0:
            secret_types = list(set(parse_secret_type(s) for s in all_secrets))
            status = f"🔴 {num_secrets} issue(s) found (Types: {', '.join(secret_types)})"
            recommendations.append(f"Review the found secret(s) in `{os.path.basename(secrets_file)}`.")
        else:
            status = "✅ 0 issues found"
        report_parts.append(f"*   **Secrets Found:** {status}")

    except (IOError, json.JSONDecodeError):
        report_parts.append("*   **Secrets Found:** Error analyzing secrets.")

    # Static Code Analysis (Bandit)
    try:
        with open(static_code_analysis_file) as f:
            bandit_data = json.load(f)
        num_issues = len(bandit_data.get("results", []))
        status = f"🔴 {num_issues} issue(s) found" if num_issues > 0 else "✅ 0 issues found"
        report_parts.append(f"*   **Code Vulnerabilities (Bandit):** {status}")
    except (IOError, json.JSONDecodeError):
         report_parts.append("*   **Code Vulnerabilities (Bandit):** Error analyzing static code.")

    # Dependencies (pip-audit)
    try:
        with open(dependencies_file) as f:
            deps_data = json.load(f)
        vulnerable_deps = [dep for dep in deps_data if dep.get("vulns") and len(dep["vulns"]) > 0]
        num_vulns = len(vulnerable_deps)
        status = f"🔴 {num_vulns} vulnerable dependency/ies found" if num_vulns > 0 else "✅ 0 vulnerabilities found"
        report_parts.append(f"*   **Dependency Issues:** {status}")
        if num_vulns > 0:
            for dep in vulnerable_deps:
                recommendations.append(f"Upgrade package `{dep['name']}` to fix known vulnerability.")
    except (IOError, json.JSONDecodeError):
        report_parts.append("*   **Dependency Issues:** Error analyzing dependencies.")

    # --- Recommendations Section ---
    if recommendations:
        report_parts.append("\n## 🚀 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            report_parts.append(f"{i}.  **{rec}**")

    # --- Log File Path ---
    report_parts.append("\n---\n")
    report_parts.append(f"👉 *For full details, see the log files in:*\n{log_dir}")

    # --- Write final report ---
    with open(output_file, "w") as f:
        f.write("\n".join(report_parts))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate final markdown report.")
    parser.add_argument("documentation_file")
    parser.add_argument("secrets_file")
    parser.add_argument("dependencies_file")
    parser.add_argument("static_code_analysis_file")
    parser.add_argument("output_file")
    parser.add_argument("log_dir")
    args = parser.parse_args()
    generate_report(
        args.documentation_file,
        args.secrets_file,
        args.dependencies_file,
        args.static_code_analysis_file,
        args.output_file,
        args.log_dir
    )