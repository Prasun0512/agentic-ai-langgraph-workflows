from __future__ import annotations

from typing import Any, TypedDict


class EnterpriseAgentState(TypedDict, total=False):
    request: str
    plan: list[str]
    research_notes: list[str]
    retrieved_context: list[str]
    validation_status: str
    approval_required: bool
    execution_result: str
    retry_count: int
    cost_units: float
    audit: list[str]


def _append_audit(state: EnterpriseAgentState, event: str) -> None:
    state.setdefault("audit", []).append(event)


def planner_agent(state: EnterpriseAgentState) -> EnterpriseAgentState:
    state["plan"] = ["research", "retrieve_context", "validate", "execute"]
    state["retry_count"] = state.get("retry_count", 0)
    state["cost_units"] = state.get("cost_units", 0.0) + 0.02
    _append_audit(state, "agent:planner")
    return state


def research_agent(state: EnterpriseAgentState) -> EnterpriseAgentState:
    state["research_notes"] = [
        "Classified request intent",
        "Checked approved enterprise knowledge sources",
    ]
    state["cost_units"] = state.get("cost_units", 0.0) + 0.03
    _append_audit(state, "agent:research")
    return state


def retrieval_agent(state: EnterpriseAgentState) -> EnterpriseAgentState:
    request = state["request"].lower()
    context = ["KB-001: human approval is required for high-risk actions"]
    if "policy" in request or "rag" in request:
        context.append("KB-002: answers require citation-backed retrieval")
    state["retrieved_context"] = context
    state["cost_units"] = state.get("cost_units", 0.0) + 0.04
    _append_audit(state, "agent:retrieval")
    return state


def validator_agent(state: EnterpriseAgentState) -> EnterpriseAgentState:
    request = state["request"].lower()
    high_risk = any(term in request for term in ("urgent", "payment", "medical", "legal"))
    has_context = bool(state.get("retrieved_context"))
    state["approval_required"] = high_risk or not has_context
    state["validation_status"] = "requires_approval" if state["approval_required"] else "approved"
    _append_audit(state, "agent:validator")
    return state


def human_approval(state: EnterpriseAgentState) -> EnterpriseAgentState:
    state["execution_result"] = "Queued for human approval before external write."
    _append_audit(state, "node:human_approval")
    return state


def execution_agent(state: EnterpriseAgentState) -> EnterpriseAgentState:
    state["execution_result"] = "Executed approved workflow action with audit trace."
    state["cost_units"] = state.get("cost_units", 0.0) + 0.01
    _append_audit(state, "agent:execution")
    return state


def route_after_validation(state: EnterpriseAgentState) -> str:
    return "human_approval" if state.get("approval_required") else "execution_agent"


def build_langgraph_workflow() -> Any:
    """Build a real LangGraph workflow when langgraph is installed.

    The repository keeps the dependency optional so the deterministic local demo
    remains runnable without external packages. Install `.[agentic]` to execute
    this graph with LangGraph.
    """

    try:
        from langgraph.graph import END, StateGraph
    except ImportError as exc:
        raise RuntimeError("Install optional dependency: pip install -e .[agentic]") from exc

    graph = StateGraph(EnterpriseAgentState)
    graph.add_node("planner_agent", planner_agent)
    graph.add_node("research_agent", research_agent)
    graph.add_node("retrieval_agent", retrieval_agent)
    graph.add_node("validator_agent", validator_agent)
    graph.add_node("human_approval", human_approval)
    graph.add_node("execution_agent", execution_agent)

    graph.set_entry_point("planner_agent")
    graph.add_edge("planner_agent", "research_agent")
    graph.add_edge("research_agent", "retrieval_agent")
    graph.add_edge("retrieval_agent", "validator_agent")
    graph.add_conditional_edges(
        "validator_agent",
        route_after_validation,
        {
            "human_approval": "human_approval",
            "execution_agent": "execution_agent",
        },
    )
    graph.add_edge("human_approval", END)
    graph.add_edge("execution_agent", END)
    return graph.compile()


def run_langgraph_demo(request: str) -> EnterpriseAgentState:
    workflow = build_langgraph_workflow()
    return workflow.invoke({"request": request, "audit": []})
