from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class AgentState:
    request: str
    intent: str = ""
    approved: bool = False
    result: str = ""
    audit: list[str] = field(default_factory=list)


Tool = Callable[[AgentState], AgentState]


def classify_intent(state: AgentState) -> AgentState:
    text = state.request.lower()
    if "case" in text or "ticket" in text:
        state.intent = "case_creation"
    elif "search" in text or "policy" in text or "knowledge" in text:
        state.intent = "knowledge_search"
    else:
        state.intent = "human_review"
    state.audit.append(f"classified:{state.intent}")
    return state


def knowledge_search(state: AgentState) -> AgentState:
    state.result = "Retrieved grounded knowledge response with citations."
    state.audit.append("tool:knowledge_search")
    return state


def validate_case_payload(state: AgentState) -> AgentState:
    state.audit.append("validated:case_payload")
    state.approved = "urgent" not in state.request.lower()
    return state


def create_case(state: AgentState) -> AgentState:
    state.result = "Created case payload for downstream system."
    state.audit.append("tool:create_case")
    return state


def human_review(state: AgentState) -> AgentState:
    state.result = "Routed to human review with full audit trace."
    state.audit.append("route:human_review")
    return state


def run_workflow(request: str) -> AgentState:
    state = classify_intent(AgentState(request=request))

    if state.intent == "knowledge_search":
        return knowledge_search(state)

    if state.intent == "case_creation":
        state = validate_case_payload(state)
        if state.approved:
            return create_case(state)
        return human_review(state)

    return human_review(state)
