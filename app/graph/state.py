from typing import TypedDict, Optional

from app.models.resume import ResumeData


class ResumeState(TypedDict, total=False):
    resume_data: ResumeData
    generated_resume: dict
    filename: str
    file_url: str
    editor_url: str

    missing_fields: list[str]
    is_complete: bool

    guardrail_passed: bool
    guardrail_violations: list[str]

    error: Optional[str]