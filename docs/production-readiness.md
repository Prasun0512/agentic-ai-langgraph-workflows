# Production Readiness

## Deployment

- Package the workflow API as a stateless service.
- Persist graph state in PostgreSQL, Redis, or a LangGraph checkpoint backend.
- Keep secrets in a managed vault, never in `.env` files committed to git.

## Security

- Restrict tools by agent node.
- Require human approval before sensitive writes.
- Capture audit events for planner, retrieval, validation, and execution nodes.

## Observability

- Emit structured logs with request IDs and node names.
- Track node latency, retry count, review rate, and estimated cost units.
- Add OpenTelemetry spans around each graph node in production.

## Cost Controls

- Use cheaper models for routing and validation.
- Set token budgets per request.
- Cache retrieval results for repeated workflow context.

## Scalability

- Keep agents stateless except for checkpointed graph state.
- Use queues for long-running or external tool actions.
- Add retry budgets and DLQ handling for failed tool calls.
