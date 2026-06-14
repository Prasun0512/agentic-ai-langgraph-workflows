from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable


@dataclass(frozen=True)
class KnowledgeDocument:
    doc_id: str
    title: str
    text: str
    tags: tuple[str, ...]


@dataclass
class AgentState:
    request: str
    intent: str = ""
    risk_level: str = "low"
    approved: bool = False
    result: str = ""
    next_action: str = ""
    citations: list[str] = field(default_factory=list)
    tool_results: dict[str, str] = field(default_factory=dict)
    audit: list[str] = field(default_factory=list)


Tool = Callable[[AgentState], AgentState]


DEFAULT_KNOWLEDGE_BASE = (
    KnowledgeDocument(
        doc_id="KB-001",
        title="Leave eligibility policy",
        text="Employees can request planned leave through the HR portal.",
        tags=("hr", "policy", "leave"),
    ),
    KnowledgeDocument(
        doc_id="KB-002",
        title="Case creation playbook",
        text="Cases require a title, category, priority, requester, and source trace.",
        tags=("case", "ticket", "support"),
    ),
    KnowledgeDocument(
        doc_id="KB-003",
        title="AI governance review",
        text="High-impact or urgent automation should route through human review.",
        tags=("governance", "review", "risk"),
    ),
)


def _tokens(text: str) -> set[str]:
    return {token.strip(".,:;!?()[]{}").lower() for token in text.split() if token}


def classify_intent(state: AgentState) -> AgentState:
    text = state.request.lower()
    if any(term in text for term in ("case", "ticket", "claim", "incident")):
        state.intent = "case_creation"
    elif any(term in text for term in ("search", "policy", "knowledge", "summarize")):
        state.intent = "knowledge_search"
    else:
        state.intent = "human_review"

    state.risk_level = assess_risk(text)
    state.audit.append(f"classified:{state.intent}")
    state.audit.append(f"risk:{state.risk_level}")
    return state


def assess_risk(text: str) -> str:
    high_risk_terms = ("urgent", "escalation", "legal", "payment", "medical")
    medium_risk_terms = ("customer", "claim", "attachment", "pii", "personal")
    if any(term in text for term in high_risk_terms):
        return "high"
    if any(term in text for term in medium_risk_terms):
        return "medium"
    return "low"


def retrieve_documents(
    query: str,
    documents: Iterable[KnowledgeDocument] = DEFAULT_KNOWLEDGE_BASE,
    limit: int = 2,
) -> list[KnowledgeDocument]:
    query_tokens = _tokens(query)
    ranked: list[tuple[int, KnowledgeDocument]] = []
    for document in documents:
        document_tokens = _tokens(" ".join((document.title, document.text, " ".join(document.tags))))
        overlap = len(query_tokens.intersection(document_tokens))
        if overlap:
            ranked.append((overlap, document))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [document for _, document in ranked[:limit]]


def knowledge_search(state: AgentState) -> AgentState:
    documents = retrieve_documents(state.request)
    state.citations = [document.doc_id for document in documents]
    if not documents:
        state.result = "No grounded answer found. Routed to human review."
        state.next_action = "human_review"
        state.audit.append("tool:knowledge_search:no_hits")
        return state

    summary = "; ".join(f"{document.title}: {document.text}" for document in documents)
    state.result = f"Grounded response prepared from {len(documents)} source(s). {summary}"
    state.next_action = "respond"
    state.audit.append("tool:knowledge_search")
    return state


def validate_case_payload(state: AgentState) -> AgentState:
    required_signals = ("case", "ticket", "claim", "incident", "support")
    has_case_signal = any(signal in state.request.lower() for signal in required_signals)
    state.approved = has_case_signal and state.risk_level != "high"
    state.audit.append("validated:case_payload")
    if not state.approved:
        state.next_action = "human_review"
        state.audit.append("approval_gate:blocked")
    return state


def create_case(state: AgentState) -> AgentState:
    case_id = f"CASE-{abs(hash(state.request)) % 100000:05d}"
    state.tool_results["case_id"] = case_id
    state.result = f"Created draft case {case_id} with audit trace and source request."
    state.next_action = "case_created"
    state.audit.append("tool:create_case")
    return state


def human_review(state: AgentState) -> AgentState:
    state.result = "Routed to human review with full audit trace and risk context."
    state.next_action = "review_queue"
    state.audit.append("route:human_review")
    return state


class AgentWorkflow:
    """Small local graph runner that mirrors LangGraph-style node routing."""

    def __init__(self) -> None:
        self.nodes: dict[str, Tool] = {
            "classify": classify_intent,
            "knowledge_search": knowledge_search,
            "validate_case": validate_case_payload,
            "create_case": create_case,
            "human_review": human_review,
        }

    def invoke(self, request: str) -> AgentState:
        state = self.nodes["classify"](AgentState(request=request))

        if state.intent == "knowledge_search":
            state = self.nodes["knowledge_search"](state)
            if state.next_action == "human_review":
                return self.nodes["human_review"](state)
            return state

        if state.intent == "case_creation":
            state = self.nodes["validate_case"](state)
            if state.approved:
                return self.nodes["create_case"](state)
            return self.nodes["human_review"](state)

        return self.nodes["human_review"](state)


def run_workflow(request: str) -> AgentState:
    return AgentWorkflow().invoke(request)
