# Security and Governance

## Agent Safety Controls

- Keep tool permissions narrow and explicit.
- Require human approval before external writes or high-risk actions.
- Validate inputs and outputs at each state transition.
- Record prompts, tool calls, decisions, risk flags, and approvals in an audit trace.

## Hallucination Reduction

- Route unsupported claims to review.
- Prefer retrieved evidence over unconstrained generation.
- Use validator checks for missing context and conflicting evidence.
- Keep deterministic tests for workflow routing and review thresholds.

## Cost and Abuse Controls

- Apply request budgets, model-routing policies, and retry limits.
- Cache stable lookups where appropriate.
- Capture token/cost telemetry in production deployments.
- Disable sensitive tools in local demo mode.

## Data Handling

This repo uses sanitized demo inputs only. Do not commit secrets, production prompts, customer documents, credentials, or private tool payloads.
