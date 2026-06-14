import unittest

from src.workflow import AgentState, execute_with_retry, run_workflow


class WorkflowTests(unittest.TestCase):
    def test_knowledge_request_uses_search_tool(self) -> None:
        state = run_workflow("search policy")
        self.assertEqual(state.intent, "knowledge_search")
        self.assertIn("tool:knowledge_search", state.audit)
        self.assertTrue(state.citations)

    def test_urgent_case_routes_to_review(self) -> None:
        state = run_workflow("create urgent case")
        self.assertEqual(state.intent, "case_creation")
        self.assertEqual(state.risk_level, "high")
        self.assertIn("route:human_review", state.audit)

    def test_normal_case_creates_case_with_audit_trace(self) -> None:
        state = run_workflow("create support case for customer access issue")
        self.assertEqual(state.next_action, "case_created")
        self.assertIn("case_id", state.tool_results)
        self.assertIn("tool:create_case", state.audit)

    def test_failed_tool_retries_and_routes_to_review(self) -> None:
        def failing_tool(state: AgentState) -> AgentState:
            raise RuntimeError("simulated outage")

        state = execute_with_retry(failing_tool, AgentState("create support case"), max_attempts=2)

        self.assertEqual(state.next_action, "review_queue")
        self.assertIn("retry:exhausted", state.audit)
        self.assertIn("route:human_review", state.audit)


if __name__ == "__main__":
    unittest.main()
