from pathlib import Path
from uuid import uuid4

from docxtpl import DocxTemplate

from app.models.resume import ResumeData
from app.validators.resume_validator import (
    is_no_experience,
)


TEMPLATE_PATH = Path(
    "templates/resume_template.docx"
)

OUTPUT_DIR = Path(
    "storage/documents"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def _clean_lines(
    values: list[str],
) -> list[str]:
    return [
        str(value).strip()
        for value in values
        if str(value).strip()
    ]


def build_resume_document(
    data: ResumeData,
    generated_resume: dict,
) -> str:
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Resume template not found: {TEMPLATE_PATH}"
        )

    skills = _clean_lines(
        generated_resume.get(
            "skills",
            [],
        )
    )

    projects = _clean_lines(
        generated_resume.get(
            "projects",
            [],
        )
    )

    contact_parts = [
        data.email.strip(),
        data.phone.strip(),
        data.location.strip(),
    ]

    contact_line = " | ".join(
        part
        for part in contact_parts
        if part
    )

    # ---------------------------------
    # Experience handling
    # ---------------------------------

    experience = generated_resume.get(
        "experience",
        "",
    ).strip()

    if is_no_experience(
        data.experience
    ):
        experience = ""

    context = {
        "name":
            data.name.strip(),

        "professional_title":
            generated_resume.get(
                "professional_title",
                data.field,
            ).strip(),

        "contact_line":
            contact_line,

        "summary":
            generated_resume.get(
                "summary",
                "",
            ).strip(),

        "skills_text":
            " • ".join(
                skills
            ),

        "education":
            generated_resume.get(
                "education",
                data.education,
            ).strip(),

        "experience":
            experience,

        "projects_text":
            "\n".join(
                f"• {project}"
                for project in projects
            ),
    }

    template = DocxTemplate(
        TEMPLATE_PATH
    )

    template.render(
        context
    )

    safe_name = "".join(
        char
        for char in (
            data.name
            .strip()
            .replace(
                " ",
                "_",
            )
        )
        if (
            char.isalnum()
            or char in {
                "_",
                "-",
            }
        )
    ) or "resume"

    filename = (
        f"{safe_name}_resume_"
        f"{uuid4().hex[:8]}.docx"
    )

    output_path = (
        OUTPUT_DIR
        / filename
    )

    template.save(
        output_path
    )

    return filename


def update_resume_document(
    filename: str,
    edited_resume: dict,
) -> str:
    """
    Re-render an existing generated resume using
    the Nova editor content.

    The same DOCX filename is overwritten.
    """

    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(
            f"Resume template not found: {TEMPLATE_PATH}"
        )

    safe_filename = (
        Path(filename).name
    )

    if not safe_filename.lower().endswith(
        ".docx"
    ):
        raise ValueError(
            "Only DOCX resume files can be updated."
        )

    output_path = (
        OUTPUT_DIR
        / safe_filename
    )

    skills = _clean_lines(
        edited_resume.get(
            "skills",
            [],
        )
    )

    projects = _clean_lines(
        edited_resume.get(
            "projects",
            [],
        )
    )

    contact_parts = [
        edited_resume
        .get(
            "email",
            "",
        )
        .strip(),

        edited_resume
        .get(
            "phone",
            "",
        )
        .strip(),

        edited_resume
        .get(
            "location",
            "",
        )
        .strip(),
    ]

    contact_line = " | ".join(
        part
        for part in contact_parts
        if part
    )

    # Allow the editor to remove experience
    # completely by leaving the field blank.
    experience = (
        edited_resume
        .get(
            "experience",
            "",
        )
        .strip()
    )

    context = {
        "name":
            edited_resume
            .get(
                "name",
                "",
            )
            .strip(),

        "professional_title":
            edited_resume
            .get(
                "professional_title",
                "",
            )
            .strip(),

        "contact_line":
            contact_line,

        "summary":
            edited_resume
            .get(
                "summary",
                "",
            )
            .strip(),

        "skills_text":
            " • ".join(
                skills
            ),

        "experience":
            experience,

        "projects_text":
            "\n".join(
                f"• {project}"
                for project in projects
            ),

        "education":
            edited_resume
            .get(
                "education",
                "",
            )
            .strip(),
    }

    template = DocxTemplate(
        TEMPLATE_PATH
    )

    template.render(
        context
    )

    template.save(
        output_path
    )

    return safe_filename