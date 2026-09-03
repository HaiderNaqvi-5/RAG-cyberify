from app.graph.state import ResumeState
from app.services.resume_ai import generate_resume_content
from app.services.resume_generator import build_resume_document
from app.guardrails.resume_guardrails import (
    validate_generated_resume,
)


def check_missing_fields(
    state: ResumeState,
) -> ResumeState:
    data = state["resume_data"]

    required_fields = [
        "name",
        "email",
        "phone",
        "location",
        "field",
        "education",
        "skills",
        "experience",
        "projects",
        "experience_level",
        "employment_status",
    ]

    missing_fields = []

    for field in required_fields:
        value = getattr(
            data,
            field,
            None,
        )

        if (
            value is None
            or not str(value).strip()
        ):
            missing_fields.append(
                field
            )

    return {
        "missing_fields":
            missing_fields,
        "is_complete":
            len(missing_fields) == 0,
    }


def generate_ai_resume(
    state: ResumeState,
) -> ResumeState:
    data = state["resume_data"]

    try:
        generated_resume = (
            generate_resume_content(
                data
            )
        )

        return {
            "generated_resume":
                generated_resume,
            "error": None,
        }

    except Exception as exc:
        return {
            "generated_resume": None,
            "error":
                f"AI generation failed: {exc}",
        }


def validate_ai_resume(
    state: ResumeState,
) -> ResumeState:
    data = state["resume_data"]

    generated_resume = state.get(
        "generated_resume"
    )

    if not generated_resume:
        return {
            "guardrail_passed":
                False,

            "guardrail_violations": [
                "No generated resume content."
            ],

            "error": (
                "Guardrail could not validate "
                "the generated resume."
            ),
        }

    result = validate_generated_resume(
        data,
        generated_resume,
    )

    if not result["valid"]:
        violations = (
            result["violations"]
        )

        violation_text = "; ".join(
            str(item)
            for item in violations
        )

        return {
            "guardrail_passed":
                False,

            "guardrail_violations":
                violations,

            "error": (
                "Generated resume failed "
                "hallucination guardrails. "
                f"Violations: {violation_text}"
            ),
        }

    return {
        "guardrail_passed": True,
        "guardrail_violations": [],
        "error": None,
    }


def generate_document(
    state: ResumeState,
) -> ResumeState:
    data = state["resume_data"]

    generated_resume = state.get(
        "generated_resume"
    )

    if not generated_resume:
        return {
            "error": (
                "No generated resume "
                "content was found."
            ),
        }

    try:
        filename = (
            build_resume_document(
                data=data,
                generated_resume=
                    generated_resume,
            )
        )

        return {
            "filename": filename,

            "file_url":
                f"/api/files/{filename}",

            "editor_url": (
                "/static/"
                "resume-editor.html"
                f"?filename={filename}"
            ),

            "error": None,
        }

    except Exception as exc:
        return {
            "error": (
                "Document generation "
                f"failed: {exc}"
            ),
        }