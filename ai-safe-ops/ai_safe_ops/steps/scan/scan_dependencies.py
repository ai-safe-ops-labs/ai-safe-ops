import argparse
import json
import os
from pathlib import Path
import sys

# Abhängigkeiten werden jetzt über setup.py installiert
from pip_audit._audit import Auditor
from pip_audit._dependency_source import requirement, pyproject
from pip_audit._service import pypi

def scan_dependencies(dependency_file_path: str, output_file: str):
    """
    Scans the dependency file for vulnerable dependencies.
    The input `dependency_file_path` is the path to an intermediate file
    that CONTAINS the actual path to the dependency file.
    """
    
    # --- KORREKTUR HIER ---
    # Schritt 1: Lies den Pfad aus der Zwischendatei.
    try:
        with open(dependency_file_path, 'r') as f:
            actual_dependency_file = f.read().strip()
    except FileNotFoundError:
        # Falls die Zwischendatei nicht existiert (z.B. weil kein pyproject gefunden wurde).
        actual_dependency_file = ""

    # Schritt 2: Überprüfe, ob der ausgelesene Pfad gültig ist.
    if not actual_dependency_file or not os.path.exists(actual_dependency_file):
        print(f"Dependency file path not found in '{dependency_file_path}' or path is invalid. Skipping scan.")
        with open(output_file, "w") as f:
            json.dump([{"name": "No valid dependency file found", "version": "", "vulns": []}], f)
        return

    print(f"Scanning dependency file at actual path: {actual_dependency_file}")
    
    # Entscheide die Quelle basierend auf dem Dateinamen des *echten* Pfades
    if os.path.basename(actual_dependency_file) == 'requirements.txt':
        source = requirement.RequirementSource(Path(actual_dependency_file))
    else:
        source = pyproject.PyProjectSource(Path(actual_dependency_file))

    service = pypi.PyPIService()
    auditor = Auditor(service)
    results = auditor.audit(source)
    
    output = []
    for dependency, vulns in results:
        output.append({
            "name": dependency.name,
            "version": str(dependency.version),
            "vulns": [
                {
                    "id": v.id,
                    "fix_versions": [str(fv) for fv in v.fix_versions],
                    "description": v.description,
                }
                for v in vulns
            ],
        })

    with open(output_file, "w") as f:
        json.dump(output, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("dependency_file_path", help="The path to the intermediate file containing the actual dependency file path.")
    parser.add_argument("output_file", help="The path to the output file.")
    args = parser.parse_args()
    scan_dependencies(args.dependency_file_path, args.output_file)