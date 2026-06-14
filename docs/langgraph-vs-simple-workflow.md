# LangGraph vs Simple Workflow

This repository keeps a dependency-light local runner and an optional LangGraph-style implementation path.

## Use A Simple Workflow When

- The process is short and mostly deterministic.
- There are only a few routing branches.
- State can be held in memory for a local demo or lightweight service.
- You need a clear fallback that runs without external dependencies.

## Use LangGraph When

- The workflow has many nodes, branches, pauses, or retries.
- Human approval can interrupt and resume execution.
- State persistence and checkpoints are required.
- Tool calls need explicit orchestration, replay, and observability.
- Teams need to evolve planner, retriever, validator, and executor nodes independently.

## Interview Talking Point

LangGraph is valuable when agent behavior must be controlled as a workflow. A single prompt loop is faster to prototype, but graph orchestration makes state, approval gates, retries, and auditability visible.
