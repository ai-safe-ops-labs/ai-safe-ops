# AI Safe Ops Toolkit

![AI Safe Ops In Action](docs/assets/ai-safe-ops.gif)

> 🥱 **The standard toolkit for the boring-but-critical AI challenges:** Governance, Security, Guardrails, Compliance, and Regulation.

### Vision & Mission

**Vision:** To become the standard toolkit for AI developers, making governance, security, and compliance simple, fast, and accessible.

**Mission:** We are building an open-source framework that acts as the "AI Framework for the boring, but important topics." It helps developers automatically audit their agentic systems and prepare them for regulations like the EU AI Act.

### Target Audience
AI Engineers developing AI agent systems with frameworks like: 
- [langchain](https://github.com/langchain-ai/langchain) & [langgraph](https://github.com/langchain-ai/langgraph)
- [Google Agent Development Kit](https://github.com/google/adk-python)
- [crewAI](https://github.com/crewAIInc/crewAI)
- [agno](https://github.com/agno-agi/agno)

seeking for a solution covering all "boring" topics like: 
- Governance
- Security
- Guardrails
- Compliance
- Regulation

## 📜 Core Philosophy: Deterministic First, AI Second

Our central principle is to provide a foundation of trust and reliability.

1.  **Deterministic First:** The majority of our checks are fast, reliable, and run completely offline using established tools. Your code and data never leave your machine.
2.  **AI Second:** We use AI-powered analysis as an optional, clearly-marked "power feature" for complex, interpretive tasks like compliance audits, where nuance is required.

## 🛠️ The Toolkit: Three Pillars of Agent Governance

AI Safe Ops is a single Python library that provides two core functions, all accessible through one intuitive Command Line Interface (CLI).

### 1. 🖥️ The CLI (`ai-safe-ops-cli`)

The central cockpit for developers. Built with Go and `bubbletea`, it provides a modern, interactive TUI to run all checks, audits, and reports. All functionality of the toolkit is exposed through this single interface.

### 2. 🔍 The Audit & Checkup Engine (Static Analysis)

This engine analyzes your agent's codebase *before* it runs. It operates in two modes:

*   **Blueprint Checkups:** Fast, deterministic scans based on pre-defined checklists (`.json` files). They are perfect for catching common issues in CI/CD pipelines.
    *   **Use Case:** Automatically scan for leaked secrets, vulnerable dependencies, and missing documentation on every code commit.
    *   **Command:** `ai-safe-ops checkup --blueprint security-essentials ./my-agent-project`

*   **Policy Audits:** Deeper, AI-powered audits that evaluate your codebase against complex regulatory or custom compliance rules defined in simple YAML files (`policy.yml`).
    *   **Use Case:** Generate a compliance report for the EU AI Act by having an AI agent analyze your code and documentation against the official requirements.
    *   **Command:** `ai-safe-ops audit --policy ./policies/eu-ai-act.yml ./my-agent-project`

### 3. 🛡️ The Guardrails Engine (Runtime Protection)

Easily implement guardrails directly into your agent's code. It acts like an airbag or ABS system, actively preventing harmful behavior in real-time.

*   **Use Case:** Prevent your agent from processing prompts containing Personal Identifiable Information (PII) or from generating responses that mention a competitor's name.
*   **Integration:** Designed to be easily plugged into the callback systems of modern agent frameworks (e.g., Google ADK's `before_model_callback`).
*   **Observability:** All Guardrail actions are instrumented with **OpenTelemetry**, allowing you to monitor and alert on agent behavior in your existing observability platforms (Datadog, Honeycomb, etc.).

**Example Guardrail Implementation:**
```python
# main.py of your agent
from ai_safe_ops.guardrails import GuardrailManager
from adk.callbacks import before_model_callback

# Initialize once
guardrail_manager = GuardrailManager(config_path="guardrails.yml")

@before_model_callback
def input_guardrail(prompt: str) -> str:
    # Check the input against your defined rules
    result = guardrail_manager.check_input(prompt)
    if result.is_blocked:
        raise ValueError(f"Input blocked by Guardrail: {result.reason}")
    return result.sanitized_text # Return the potentially redacted prompt
```

## 🗺️ Roadmap & Current Status

This is a living document that tracks our progress. Completed items are checked.

### Phase 1: Foundation & Deterministic Scans (The "Checkup Engine")

**Goal:** Provide a robust, offline-first engine for baseline security and quality checks.

*   [x] **CLI:** A fully interactive Go-based TUI to orchestrate all operations.
*   [x] **Ingestion:** Standardize codebase analysis using `repomix`.
*   [x] **Security Scans:** Integrate `detect-secrets`, `bandit` (static code analysis), and `pip-audit` (dependency vulnerabilities).
*   [x] **Governance Scans:** Implement checks for documentation (`README`, `LICENSE`), potential PII exposure, and misconfigurations in `.yaml` and `.json` files.
*   [x] **Ethical Heuristics:** A `spaCy`-based scan to detect potentially biased language in comments and code.
*   [x] **Reporting:** A modular system to generate clear, actionable Markdown reports.
*   [x] **Blueprint Engine:** A flexible JSON-based system to define and run sequences of checkup steps.

### Phase 2: The Guardrails Library (Runtime Protection)

**Goal:** Deliver the first version of the real-time protection library.

*   [ ] **Refactor Core Structure:** Reorganize the `ai_safe_ops` Python package to clearly separate the `audit_engine` and the `guardrails` library modules.
*   [ ] **Establish `guardrails.yml` Schema:** Define the YAML structure for defining guardrails (e.g., rule name, type `[entity_ruler, phrase_matcher]`, patterns, action `[block, redact]`).
*   [ ] **Implement `GuardrailManager`:** Create the core class in `ai_safe_ops.guardrails` that loads and parses a `guardrails.yml` file.
*   [ ] **`spaCy` Integration:** Implement the logic that dynamically builds a `spaCy` pipeline based on the rules defined in the YAML file.
*   [ ] **Develop Core Check Methods:** Create the `check_input()` and `check_output()` methods that process text and return a structured result object.
*   [ ] **Integrate OpenTelemetry:** Instrument the `GuardrailManager` to emit traces and structured logs for every check performed.
*   [ ] **Create Guardrail Templates:** Provide pre-built `guardrails.yml` files for common use cases like PII filtering.

### Phase 3: The AI-Powered Audit Engine (Compliance as Code)

**Goal:** Implement the flexible, policy-as-code audit functionality.

*   [ ] **Define `policy.yml` Schema:** Design the YAML structure for defining compliance policies, including requirements, descriptions, and the specific check prompts for the AI agent.
*   [ ] **Develop `run_ai_compliance_audit` Step:** Create a new Python step for the audit engine that takes a codebase context and a `policy.yml` file as input.
*   [ ] **Implement the PydanticAI Auditor:** Build the core AI agent that systematically works through the checks in the policy file, analyzes the code, and generates a structured JSON output with its findings and evidence.
*   [ ] **Create EU AI Act Policy:** As the first reference implementation, create a `eu-ai-act.yml` policy based on the technical requirements from `compl-ai.org`.
*   [ ] **Report Generation:** Enhance the report generation step to display the qualitative results from the AI audit.

### Phase 4: Ecosystem & Usability

**Goal:** Lower the barrier to entry and foster a community around the toolkit.

*   [ ] **CI/CD Integration Guides:** Create template configurations for integrating `ai-safe-ops checkup` into GitHub Actions and GitLab CI.
*   [ ] **Documentation:** Write comprehensive guides on how to integrate Guardrails and create custom Policies.
*   [ ] **Expanded Blueprint & Policy Library:** Develop and share more pre-built blueprints and policies based on community feedback.

## 🤝 Contributing

We welcome contributions! Please see our (forthcoming) `CONTRIBUTING.md` for guidelines on how to submit issues, feature requests, and pull requests.

## 📄 License

This project is licensed under the Apache 2.0 License. See the `LICENSE` file for details.