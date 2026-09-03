from typing import Literal

from pydantic import BaseModel, field_validator

from app.validators.resume_validator import (
    clean_comma_separated,
    clean_phone,
    clean_text,
    validate_email,
    validate_location,
    validate_phone,
)


class ResumeData(BaseModel):
    name: str
    email: str
    phone: str
    location: str
    field: str
    education: str
    skills: str
    experience: str
    projects: str

    # Multiple-choice fields
    experience_level: Literal[
        "student",
        "entry_level",
        "mid_level",
        "senior",
    ]

    employment_status: Literal[
        "studying",
        "employed",
        "unemployed",
    ]

    @field_validator(
        "name",
        "field",
        "education",
        "experience",
        "projects",
        mode="before",
    )
    @classmethod
    def clean_normal_text(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Value must be text."
            )

        cleaned = clean_text(value)

        if not cleaned:
            raise ValueError(
                "This field cannot be empty."
            )

        return cleaned

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def validate_and_clean_email(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Email must be text."
            )

        cleaned = clean_text(value)

        if not validate_email(cleaned):
            raise ValueError(
                "Invalid email address."
            )

        return cleaned

    @field_validator(
        "phone",
        mode="before",
    )
    @classmethod
    def validate_and_clean_phone(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Phone must be text."
            )

        cleaned = clean_phone(value)

        if not validate_phone(cleaned):
            raise ValueError(
                "Invalid Pakistani mobile number. "
                "Use 03123456751 or +923124234567."
            )

        return cleaned

    @field_validator(
        "location",
        mode="before",
    )
    @classmethod
    def validate_and_clean_location(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Location must be text."
            )

        cleaned = clean_text(value)

        if not validate_location(cleaned):
            raise ValueError(
                "Invalid location. "
                "Example: Multan or Lahore, Pakistan."
            )

        return cleaned

    @field_validator(
        "skills",
        mode="before",
    )
    @classmethod
    def clean_skills(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Skills must be text."
            )

        cleaned = clean_comma_separated(
            value
        )

        if not cleaned:
            raise ValueError(
                "Skills cannot be empty."
            )

        return cleaned


class GeneratedResume(BaseModel):
    professional_title: str
    summary: str
    skills: list[str]
    education: str
    experience: str
    projects: list[str]


class EditedResume(BaseModel):
    filename: str
    name: str
    professional_title: str
    email: str
    phone: str
    location: str
    summary: str
    skills: list[str]
    experience: str
    projects: list[str]
    education: str

    @field_validator(
        "filename",
        "name",
        "professional_title",
        "summary",
        "experience",
        "education",
        mode="before",
    )
    @classmethod
    def clean_edited_text(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Value must be text."
            )

        cleaned = clean_text(value)

        if not cleaned:
            raise ValueError(
                "This field cannot be empty."
            )

        return cleaned

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def validate_edited_email(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Email must be text."
            )

        cleaned = clean_text(value)

        if not validate_email(cleaned):
            raise ValueError(
                "Invalid email address."
            )

        return cleaned

    @field_validator(
        "phone",
        mode="before",
    )
    @classmethod
    def validate_edited_phone(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Phone must be text."
            )

        cleaned = clean_phone(value)

        if not validate_phone(cleaned):
            raise ValueError(
                "Invalid Pakistani mobile number. "
                "Use 03123456751 or +923124234567."
            )

        return cleaned

    @field_validator(
        "location",
        mode="before",
    )
    @classmethod
    def validate_edited_location(
        cls,
        value,
    ):
        if not isinstance(value, str):
            raise ValueError(
                "Location must be text."
            )

        cleaned = clean_text(value)

        if not validate_location(cleaned):
            raise ValueError(
                "Invalid location. "
                "Example: Multan or Lahore, Pakistan."
            )

        return cleaned

    @field_validator(
        "skills",
        mode="before",
    )
    @classmethod
    def validate_edited_skills(
        cls,
        value,
    ):
        if not isinstance(value, list):
            raise ValueError(
                "Skills must be a list."
            )

        cleaned = [
            clean_text(str(skill))
            for skill in value
            if clean_text(str(skill))
        ]

        if not cleaned:
            raise ValueError(
                "At least one skill is required."
            )

        return cleaned

    @field_validator(
        "projects",
        mode="before",
    )
    @classmethod
    def validate_edited_projects(
        cls,
        value,
    ):
        if not isinstance(value, list):
            raise ValueError(
                "Projects must be a list."
            )

        return [
            clean_text(str(project))
            for project in value
            if clean_text(str(project))
        ]