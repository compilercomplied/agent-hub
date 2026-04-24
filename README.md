# Agent Hub

Agent hub is an AI agent orchestrator. It integrates with LLM http APIs using the ReAct pattern to enable fully autonomous agent workflows with Human In The Loop checks.

These are the AI workloads the project is able to run:
 - Autonomous coding tasks. To do this, agent-hub deploys a pod using the [agent-dev-environment](https://github.com/compilercomplied/agent-dev-environment) headless service. This service contains all the configuration needed for a sandboxed environment that can be manipulated and interacted with through http.

# Rutime view

This is deployed through pulumi and github workflows. The main non-obvious bits are:
 - Secrets. There are a few important secrets, you can check these in the pulumi templates. KUBECONFIG is encoded as base64 and injected so agent-hub can deploy pods with containerized environments.
 - Containerized workloads. agent-hub acts as a kubernetes orchestrator. It deploys pods on demand based on user tasks.
 - Containerized workload configuration. agent-hub does not configure the underlying headless services or kubernetes components. It merely deploys them.


# Development
## Mise

[mise](https://mise.jdx.dev/) is used to manage tool versions and abstract common tasks. It is installed in the Docker image and available at runtime.

## Prerequisites

- [mise](https://mise.jdx.dev/) installed.

## Running locally

On your first run:
```bash
# Install tools
mise install

# Configure project
mise setup-project
```

The project is aimed to be run through e2e tests. So you can use either e2e command in the mise.toml (running the e2e with or without docker).
