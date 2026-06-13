import unittest

from src.workflow import run_workflow


class WorkflowTests(unittest.TestCase):
    def test_knowledge_request_uses_search_tool(self) -> None:
        state = run_workflow("search policy")
        self.assertEqual(state.intent, "knowledge_search")
        self.assertIn("tool:knowledge_search", state.audit)

    def test_urgent_case_routes_to_review(self) -> None:
        state = run_workflow("create urgent case")
        self.assertEqual(state.intent, "case_creation")
        self.assertIn("route:human_review", state.audit)


if __name__ == "__main__":
    unittest.main()
