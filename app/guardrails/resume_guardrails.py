import re


def normalize_text(value: str) -> str:
    value = str(value or "").lower()

    value = re.sub(
        r"[^a-z0-9+#.\s-]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def get_value(obj, key, default=""):
    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(
        obj,
        key,
        default,
    )


def extract_numbers(text: str) -> set[str]:
    return set(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            str(text or ""),
        )
    )


def validate_generated_resume(
    source_data,
    generated_resume,
) -> dict:
    violations = []

    # ---------------------------------
    # Build complete user source text
    # ---------------------------------

    source_fields = [
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

    source_parts = []

    for field in source_fields:
        value = get_value(
            source_data,
            field,
            "",
        )

        if value:
            source_parts.append(
                str(value)
            )

    source_text = " ".join(
        source_parts
    )

    source_normalized = (
        normalize_text(
            source_text
        )
    )

    # ---------------------------------
    # Check generated skills
    # ---------------------------------

    generated_skills = get_value(
        generated_resume,
        "skills",
        [],
    )

    if isinstance(
        generated_skills,
        str,
    ):
        generated_skills = [
            generated_skills
        ]

    for skill in generated_skills:
        normalized_skill = (
            normalize_text(skill)
        )

        if (
            normalized_skill
            and normalized_skill
            not in source_normalized
        ):
            violations.append(
                f"Unsupported skill: {skill}"
            )

    # ---------------------------------
    # Prevent invented numbers
    # ---------------------------------

    generated_parts = [
        get_value(
            generated_resume,
            "professional_title",
            "",
        ),
        get_value(
            generated_resume,
            "summary",
            "",
        ),
        get_value(
            generated_resume,
            "education",
            "",
        ),
        get_value(
            generated_resume,
            "experience",
            "",
        ),
    ]

    projects = get_value(
        generated_resume,
        "projects",
        [],
    )

    if isinstance(projects, list):
        generated_parts.extend(
            str(project)
            for project in projects
        )
    else:
        generated_parts.append(
            str(projects)
        )

    generated_text = " ".join(
        str(value)
        for value in generated_parts
    )

    source_numbers = (
        extract_numbers(
            source_text
        )
    )

    generated_numbers = (
        extract_numbers(
            generated_text
        )
    )

    unsupported_numbers = (
        generated_numbers
        - source_numbers
    )

    for number in sorted(
        unsupported_numbers
    ):
        violations.append(
            f"Unsupported number or metric: {number}"
        )

    return {
        "valid":
            len(violations) == 0,

        "violations":
            violations,
    }