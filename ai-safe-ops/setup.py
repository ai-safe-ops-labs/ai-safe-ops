from setuptools import setup, find_packages

setup(
    name="ai-safe-ops",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "repomix",
        "opentelemetry-api",
        "opentelemetry-sdk",
        "opentelemetry-exporter-otlp-proto-http",
        "pip-audit",
        "detect-secrets",
        "bandit",
        "pyyaml",
        "spacy",
    ],
    author="AI SafeOps Labs",
    description="A modular framework for analyzing, classifying, and certifying AI codebases."
)