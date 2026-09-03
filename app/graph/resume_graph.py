from langgraph.graph import StateGraph, END

from app.graph.state import ResumeState
from app.graph.nodes import (
    check_missing_fields,
    generate_ai_resume,
    validate_ai_resume,
    generate_document,
)


def route_after_validation(
    state: ResumeState,
) -> str:

    if state.get("error"):
        return "end"

    if not state.get(
        "is_complete",
        False,
    ):
        return "end"

    return "generate_ai"


def route_after_ai(
    state: ResumeState,
) -> str:

    if state.get("error"):
        return "end"

    if not state.get(
        "generated_resume"
    ):
        return "end"

    return "validate_ai"


def route_after_guardrail(
    state: ResumeState,
) -> str:

    if state.get("error"):
        return "end"

    if not state.get(
        "guardrail_passed",
        False,
    ):
        return "end"

    return "generate_document"


def build_resume_graph():

    graph = StateGraph(
        ResumeState
    )

    graph.add_node(
        "check_missing_fields",
        check_missing_fields,
    )

    graph.add_node(
        "generate_ai_resume",
        generate_ai_resume,
    )

    graph.add_node(
        "validate_ai_resume",
        validate_ai_resume,
    )

    graph.add_node(
        "generate_document",
        generate_document,
    )

    graph.set_entry_point(
        "check_missing_fields"
    )

    graph.add_conditional_edges(
        "check_missing_fields",
        route_after_validation,
        {
            "generate_ai":
                "generate_ai_resume",

            "end":
                END,
        },
    )

    graph.add_conditional_edges(
        "generate_ai_resume",
        route_after_ai,
        {
            "validate_ai":
                "validate_ai_resume",

            "end":
                END,
        },
    )

    graph.add_conditional_edges(
        "validate_ai_resume",
        route_after_guardrail,
        {
            "generate_document":
                "generate_document",

            "end":
                END,
        },
    )

    graph.add_edge(
        "generate_document",
        END,
    )

    return graph.compile()


resume_graph = build_resume_graph()