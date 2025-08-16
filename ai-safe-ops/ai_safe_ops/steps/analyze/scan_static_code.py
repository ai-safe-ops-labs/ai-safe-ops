import argparse
import json
import os
import subprocess
import sys

def scan_static_code(codebase_path: str, output_file: str):
    """
    Performs static code analysis using Bandit to find common security issues.
    
    Args:
        codebase_path: The absolute path to the codebase to scan.
        output_file: The file path to write the JSON results to.
    """
    if not os.path.isdir(codebase_path):
        raise ValueError(f"Provided codebase path is not a valid directory: {codebase_path}")

    # The command to run Bandit.
    # -r: recursive
    # -f json: format output as JSON
    # -o -: pipe output to stdout
    command = [
        sys.executable,
        "-m",
        "bandit",
        "-r",
        codebase_path,
        "-f",
        "json",
        "-o",
        output_file,
        "--exit-zero" # Always exit with 0, even if issues are found. We handle the results.
    ]

    try:
        print(f"Running static code analysis on {codebase_path}...")
        # We don't need to capture output here as Bandit can write directly to the file.
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        # Optional: Log stdout/stderr for debugging
        log_dir = os.path.dirname(output_file)
        with open(os.path.join(log_dir, "bandit_stdout.log"), "w") as f:
            f.write(result.stdout)
        if result.stderr:
             with open(os.path.join(log_dir, "bandit_stderr.log"), "w") as f:
                f.write(result.stderr)

        print("Static code analysis completed successfully.")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        # This will now be caught by Go and displayed in the TUI
        error_message = f"Bandit execution failed. Stderr: {e.stderr if hasattr(e, 'stderr') else 'Command not found. Is bandit installed?'}"
        # Write an empty result file to avoid breaking the workflow
        with open(output_file, "w") as f:
            json.dump({"error": error_message}, f)
        # Re-raise to let the main workflow know something went wrong
        raise Exception(error_message) from e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Bandit static code analysis.")
    parser.add_argument("codebase_path", help="The path to the codebase to analyze.")
    parser.add_argument("output_file", help="The path to save the JSON report.")
    args = parser.parse_args()
    scan_static_code(args.codebase_path, args.output_file)