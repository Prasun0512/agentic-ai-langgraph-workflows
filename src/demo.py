from .workflow import run_workflow


def main() -> None:
    examples = [
        "Search HR policy for leave eligibility",
        "Create a support case from this email",
        "Create an urgent case that needs approval",
    ]
    for request in examples:
        state = run_workflow(request)
        print(f"\nRequest: {request}")
        print(f"Intent: {state.intent}")
        print(f"Result: {state.result}")
        print(f"Audit: {state.audit}")


if __name__ == "__main__":
    main()
