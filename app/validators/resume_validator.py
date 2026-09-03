# app/validators/resume_validator.py

import re


EMAIL_PATTERN = re.compile(
    r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
)

LOCATION_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z\s,\-.'()]{1,80}$"
)


def clean_text(value: str) -> str:
    return re.sub(
        r"\s+",
        " ",
        value,
    ).strip()


def validate_email(
    email: str,
) -> bool:
    email = clean_text(email)

    return bool(
        EMAIL_PATTERN.fullmatch(
            email
        )
    )


def clean_phone(
    phone: str,
) -> str:
    phone = phone.strip()

    return re.sub(
        r"[\s\-\(\)]",
        "",
        phone,
    )


def validate_phone(
    phone: str,
) -> bool:
    phone = clean_phone(
        phone
    )

    local_pattern = re.compile(
        r"^03\d{9}$"
    )

    international_pattern = re.compile(
        r"^\+923\d{9}$"
    )

    return bool(
        local_pattern.fullmatch(
            phone
        )
        or
        international_pattern.fullmatch(
            phone
        )
    )


def validate_location(
    location: str,
) -> bool:
    location = clean_text(
        location
    )

    if len(location) < 2:
        return False

    if not LOCATION_PATTERN.fullmatch(
        location
    ):
        return False

    # Must contain at least two letters.
    letters = re.findall(
        r"[A-Za-z]",
        location,
    )

    return len(letters) >= 2


def is_no_experience(
    value: str,
) -> bool:
    cleaned = clean_text(
        value
    ).lower()

    no_experience_values = {
        "none",
        "no",
        "no experience",
        "no work experience",
        "no professional experience",
        "n/a",
        "na",
        "not applicable",
    }

    return (
        cleaned
        in no_experience_values
    )


def clean_comma_separated(
    value: str,
) -> str:
    items = [
        clean_text(item)
        for item in value.split(",")
        if clean_text(item)
    ]

    return ", ".join(items)


def clean_resume_data(
    data: dict,
) -> dict:
    cleaned = {}

    for key, value in data.items():
        if not isinstance(
            value,
            str,
        ):
            cleaned[key] = value
            continue

        if key == "phone":
            cleaned[key] = (
                clean_phone(value)
            )

        elif key == "skills":
            cleaned[key] = (
                clean_comma_separated(
                    value
                )
            )

        else:
            cleaned[key] = (
                clean_text(value)
            )

    return cleaned