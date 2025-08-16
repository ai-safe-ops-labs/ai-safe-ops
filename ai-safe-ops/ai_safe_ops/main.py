import json
import importlib
import argparse
import os
import sys
import uuid
from datetime import datetime

def run_workflow(workflow_file: str, workflow_inputs: dict, enable_local_logs: bool, log_dir: str = None):
    """
    Runs a workflow defined in a JSON file.
    """
    with open(workflow_file, "r") as f:
        workflow = json.load(f)

    all_step_names = [step["name"] for step in workflow["steps"]]
    print(f"ALL_STEPS:{','.join(all_step_names)}", file=sys.stdout, flush=True)

    run_id = str(uuid.uuid4())
    step = {} 

    try:
        if enable_local_logs and log_dir:
            with open(os.path.join(log_dir, "workflow_log.txt"), "a") as log_f:
                log_f.write(f"Running workflow: {workflow['name']} (Run ID: {run_id})\n")
                log_f.write(f"Log directory: {log_dir}\n")

        step_outputs = {}

        for step_data in workflow["steps"]:
            step = step_data
            print(f"STEP_START:{step['name']}", file=sys.stdout, flush=True)
            
            if enable_local_logs and log_dir:
                 with open(os.path.join(log_dir, "workflow_log.txt"), "a") as log_f:
                    log_f.write(f"Running step: {step['name']}\n")
            
            module_name = step["module"]
            function_name = step["function"]
            
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            
            inputs = {}
            for key, value in step["inputs"].items():
                if isinstance(value, str) and value.startswith("{workflow.inputs."):
                    input_key = value.replace("{workflow.inputs.", "").replace("}", "")
                    inputs[key] = workflow_inputs[input_key]
                # --- KORREKTUR HIER ---
                elif value == "{workflow.log_dir}":
                    inputs[key] = log_dir
                elif value == "{workflow.all_steps}":
                    inputs[key] = all_step_names
                elif isinstance(value, str) and value.startswith("{steps."):
                    parts = value.replace("{steps.", "").replace("}", "").split(".outputs.")
                    step_name = parts[0]
                    output_key = parts[1]
                    if key.endswith("_path") or key.endswith("_file"):
                        inputs[key] = step_outputs[step_name][output_key]
                    else:
                        with open(step_outputs[step_name][output_key], "r") as f_in:
                            inputs[key] = f_in.read().strip()
                else:
                    inputs[key] = value

            outputs = {}
            step_outputs[step['name']] = {}
            for key, value in step["outputs"].items():
                if isinstance(value, str) and value.startswith("{workflow.outputs."):
                    output_key = value.replace("{workflow.outputs.", "").replace("}", "")
                    output_dir = log_dir if enable_local_logs and log_dir else os.path.join(os.getcwd(), ".ai-safe-ops", "temp", run_id)
                    if not os.path.exists(output_dir):
                        os.makedirs(output_dir, exist_ok=True)
                    output_file = os.path.join(output_dir, f"{output_key}.txt")
                    outputs[key] = output_file
                    step_outputs[step['name']][key] = output_file
                else:
                    outputs[key] = value

            function(**inputs, **outputs)

            print(f"STEP_DONE:{step['name']}", file=sys.stdout, flush=True)
            if enable_local_logs and log_dir:
                with open(os.path.join(log_dir, "workflow_log.txt"), "a") as log_f:
                    log_f.write(f"Step '{step['name']}' completed successfully.\n")
        
        log_path_info = os.path.abspath(log_dir) if log_dir else "Disabled"
        print(f"WORKFLOW_COMPLETE:{workflow['name']};;{log_path_info}", file=sys.stdout, flush=True)

    except Exception as e:
        step_name = step.get('name', 'Unknown')
        error_message = f"Error during step '{step_name}': {e}"
        if log_dir:
            with open(os.path.join(log_dir, "workflow_log.txt"), "a") as log_f:
                import traceback
                log_f.write(f"{error_message}\n")
                traceback.print_exc(file=log_f)
        print(f"WORKFLOW_ERROR:{error_message}", file=sys.stderr, flush=True)
        raise

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("workflow_name", help="The name of the workflow JSON file.")
    parser.add_argument("path", help="The path to the codebase to analyze.")
    parser.add_argument("--enable-local-logs", action="store_true", help="Enable writing local log files.")
    parser.add_argument("--log-dir", help="The directory to store logs.", default=None)
    args = parser.parse_args()
    script_dir = os.path.dirname(__file__)
    workflow_file_path = os.path.join(script_dir, "workflows", f"{args.workflow_name}.json")
    if not os.path.exists(workflow_file_path):
        print(f"Error: Workflow file not found at {workflow_file_path}", file=sys.stderr, flush=True)
        exit(1)
    workflow_inputs = {"path": args.path}
    run_workflow(workflow_file_path, workflow_inputs, args.enable_local_logs, args.log_dir)