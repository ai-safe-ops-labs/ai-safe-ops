import os
import subprocess
import sys

def ingest_codebase(path: str, output_file: str):
    """
    Ingests the codebase using repomix to create an AI-ready overview.
    The output is written to the specified output_file.
    """
    try:
        # Sicherstellen, dass repomix installiert ist
        subprocess.run([sys.executable, "-m", "pip", "install", "repomix"], check=True, capture_output=True, text=True)
        
        command = [sys.executable, "-m", "repomix", path, "--output", os.path.abspath(output_file)]
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        
        log_dir = os.path.dirname(output_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        with open(os.path.join(log_dir, "repomix_stdout.log"), "w") as f:
            f.write(result.stdout)
        if result.stderr:
            with open(os.path.join(log_dir, "repomix_stderr.log"), "w") as f:
                f.write(result.stderr)
        
    except subprocess.CalledProcessError as e:
        log_dir = os.path.dirname(output_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
            
        with open(os.path.join(log_dir, "repomix_error_stdout.log"), "w") as f:
            f.write(e.stdout)
        with open(os.path.join(log_dir, "repomix_error_stderr.log"), "w") as f:
            f.write(e.stderr)
        raise
    except FileNotFoundError as e:
        raise Exception(f"Command not found: {e}. Is Python correctly installed and in your PATH?")