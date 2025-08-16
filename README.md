# AI Safe Ops 360 - Project Charter (Internal)

## 1. Vision & Mission

**Vision:** To become the standard toolkit for AI developers, making governance, security, and compliance simple, fast, and accessible.

**Mission:** We are building a modular and extensible open-source framework that acts as the "AI Framework for the boring, but important topics." It helps developers automatically audit their systems (especially agentic frameworks) and get them "EU Compliant"-ready.

## 2. Core Philosophy: "Deterministic First, AI Second"

Our central development principle is to implement as many checks as possible **without the use of LLMs**.

**Why?**
*   **Trust & Privacy:** The user's codebase never leaves their local machine. This is our core promise and a critical feature.
*   **Speed & Cost:** Deterministic checks are orders of magnitude faster and free to run. LLM API calls are slow and can be expensive.
*   **Reliability & Reproducibility:** The results are deterministic and free of hallucinations. The same input will always produce the same output, which is essential for compliance reporting.
*   **Pragmatic Foundation:** LLM-powered analyses can be added later as optional, clearly-marked "power features" for complex, interpretive tasks.

## 3. High-Level Architecture

The system is based on a pipeline architecture, divided into logical stages. Each `Step` is a self-contained Python script. Each `Workflow` is a JSON file that orchestrates a sequence of these Steps.

**The Pipeline Stages:**

1.  **Ingest:** Prepares the codebase for analysis (e.g., by bundling it with `repomix`).
2.  **Scan:** Extracts raw, specific information (e.g., dependency files, API key patterns, doc files). No evaluation happens at this stage.
3.  **Analyze:** Performs a technical evaluation on the raw data (e.g., CVE scan, static code analysis).
4.  **Classify:** Categorizes analysis findings into risk or compliance categories (e.g., severity, EU AI Act risk levels).
5.  **Score & Report:** Aggregates all findings, calculates metrics/scores, and generates a final, human-readable report with actionable recommendations.

## 4. Tech Stack

*   **CLI / TUI:** Go with the `charmbracelet/bubbletea` framework for a modern, interactive user experience.
*   **Core Engine & Steps:** Python. Each Step is a modular script invoked by the Go CLI.
*   **Extensibility:** Users can write their own Steps in Python and orchestrate them via custom JSON Workflows.

## 5. Roadmap

Our development is structured in phases, moving from a solid, deterministic foundation to more advanced, context-aware analyses.

### Phase 1: Foundation (Core Security & Documentation Scans)

**Goal:** Provide immediate, high-value security and transparency checks that are fast, reliable, and run completely offline.

*   [x] **Ingest:** `ingest_codebase` (with repomix)
*   [x] **Scan:** `scan_secrets` (with detect-secrets)
*   [x] **Analyze:** `scan_dependencies` (with pip-audit)
*   [x] **Analyze:** `scan_static_code` (with Bandit)
*   [ ] **Scan:** `scan_documentation` (Check for the existence and basic content of `README.md`, `LICENSE`, etc.)
*   [ ] **Report:** An improved report structure that clearly presents findings and actionable recommendations in the TUI.

### Phase 2: Governance & Deeper Insights

**Goal:** Move beyond pure security to provide deeper governance checks related to data handling, configuration, and ethical heuristics.

*   [x] **Analyze:** `scan_data_handling` (Use regex to identify potential logging of PII or sensitive information).
*   [x] **Analyze:** `scan_config_files` (Check `.yaml`/`.json` files for common misconfigurations or missing security settings).
*   [x] **Analyze:** `check_bias_heuristics` (Use NLP libraries like `spaCy` to scan comments and variable names for potentially biased or problematic language).
*   [x] **Classify:** Implement a basic risk classification step based on the findings from Phase 1 and 2.

### Phase 3: Advanced MLOps & Compliance Integration

**Goal:** Provide a holistic view of the AI system's lifecycle by integrating with the broader MLOps ecosystem.

*   [ ] **Analyze:** `analyze_test_coverage` (Integrate with tools like `pytest-cov` to report on test coverage).
*   [ ] **Traceability:** `track_model_lineage` (Integrate with tools like `MLflow` or `DVC` to check for model and data versioning).
*   [ ] **Impact:** `assess_environmental_impact` (Estimate CO2 footprint from training metrics if available in logs or metadata).
*   [ ] **Report:** Generate standardized reports (e.g., JSON, HTML) for auditing purposes.

### Future Vision & Optional Modules

*   **LLM-Powered Analysis:** Offer optional, clearly marked workflows that use `pydanticAI` and LLMs for qualitative code review, automated documentation generation, and advanced context-aware risk assessment.
*   **CI/CD Integration:** Provide templates and guides for integrating `ai-safe-ops-cli` into popular CI/CD pipelines (e.g., GitHub Actions).
*   **Custom Policies:** Allow users to define their own rule sets (e.g., via YAML files) to check for company-specific "Code of Conduct" violations or internal best practices.