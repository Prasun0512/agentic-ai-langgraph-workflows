# Evaluation Strategy

Agentic AI evaluation focuses on workflow behavior, not just answer text.

## What To Evaluate

- Correct routing from intent classifier to workflow path.
- Planner output completeness and safe scoping.
- Tool selection accuracy.
- Human approval routing for high-risk actions.
- Retry and failure behavior.
- Audit trace completeness.
- Final response grounding and unsupported-claim risk.

## Local Checks

```bash
python -m unittest discover -s tests
python -m src.demo
```

## Example Quality Gates

- High-risk actions must route through approval.
- Failed tools must record retry attempts and failure reasons.
- Final output must include enough audit context to explain the path taken.
- Unsupported or ambiguous requests should not execute external actions.

## Future Improvements

- Add golden execution traces in `examples/`.
- Add LangGraph checkpoint persistence tests.
- Add cost and latency metrics per node.
