# Security and Privacy

This document complements `docs/security-and-governance.md`.

## Agent Safety

- Keep tool permissions explicit and minimal.
- Require human approval before writes to external systems.
- Validate state before each execution step.
- Avoid autonomous destructive actions in public demos.

## Data Handling

- Use sanitized requests and tool payloads only.
- Do not commit credentials, internal APIs, real workflow payloads, or private prompts.
- Keep audit traces useful but free of sensitive data.

## Production Notes

Real deployments should use RBAC, secret management, policy enforcement, tracing, request budgets, and per-tool allowlists.
