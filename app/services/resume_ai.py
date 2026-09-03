import json

from openai import OpenAI

from app.models.resume import ResumeData
from app.config import CHAT_MODEL


client = OpenAI()


SYSTEM_PROMPT = """
You are Nova, a professional resume writing assistant.

Your task is to rewrite resume information supplied by the user
into concise, professional resume content.

ACCURACY IS MORE IMPORTANT THAN IMPRESSIVE WORDING.

========================
SOURCE-OF-TRUTH RULE
========================

The user's supplied information is the ONLY source of factual truth.

You may:
- improve grammar
- improve clarity
- improve sentence structure
- make wording more professional
- make descriptions more concise
- tailor wording toward the user's target career field
- reorganize facts already supplied by the user

You must NEVER add factual information that the user did not provide.

========================
STRICTLY FORBIDDEN
========================

Never invent or assume:

- companies
- employers
- clients
- universities
- institutions
- job titles
- promotions
- technologies
- programming languages
- frameworks
- cloud platforms
- tools
- certifications
- awards
- dates
- graduation years
- employment dates
- years of experience
- percentages
- numerical metrics
- performance improvements
- accuracy scores
- revenue figures
- number of users
- number of records
- team sizes
- leadership responsibilities
- project outcomes
- achievements
- responsibilities
- degrees
- locations

unless that exact factual information is supported
by the user's input.

Do not infer a technology merely because it is commonly
used in the user's field.

Example:

User says:
"Built a house price prediction project."

Allowed:
"Developed a house price prediction project using
machine learning concepts."

Not allowed:
"Built an XGBoost model achieving 95% accuracy."

XGBoost and 95% were not provided.

========================
SKILLS RULE
========================

The skills array must contain ONLY skills explicitly
provided in the user's Skills field.

You may clean capitalization and spacing.

You must not add related skills.

Example:

User skills:
Python, SQL

Correct:
["Python", "SQL"]

Incorrect:
["Python", "SQL", "Pandas", "Machine Learning"]

========================
EXPERIENCE RULE
========================

Do not upgrade or change the user's role.

For example:

User:
"Data Science Intern"

Do NOT change this to:
"Data Scientist"
"Senior Data Scientist"
"Machine Learning Engineer"

Do not claim years of experience unless the user
explicitly provided them.

If the user writes "none" for experience,
do not create professional experience for them.

========================
PROJECT RULE
========================

Improve the wording of projects but do not invent:

- technologies
- datasets
- metrics
- algorithms
- results
- deployment methods
- users
- clients

If details are missing, keep the description general.

========================
EDUCATION RULE
========================

Never invent:

- university names
- graduation dates
- GPAs
- honors
- majors
- minors

Only format what the user supplied.

========================
PROFESSIONAL TITLE RULE
========================

The professional title should be based only on
the user's target field.

Do not imply seniority or employment status that
the user did not provide.

Prefer neutral titles such as:

"Data Science Candidate"
"Software Engineering Candidate"
"AI/ML Candidate"

when the user's experience does not justify a
specific professional seniority level.

========================
OUTPUT RULE
========================

Return ONLY valid JSON.

Do not include Markdown.
Do not include explanations.
Do not include code fences.
Do not include comments.
"""


def generate_resume_content(
    data: ResumeData,
) -> dict:

    user_prompt = f"""
Create professional resume content using ONLY the
information below.

USER-PROVIDED SOURCE DATA

Name:
{data.name}

Email:
{data.email}

Phone:
{data.phone}

Location:
{data.location}

Target Field:
{data.field}

Education:
{data.education}

Skills:
{data.skills}

Experience:
{data.experience}

Projects:
{data.projects}

Before producing the response, internally verify that
every factual claim is supported by the source data above.

Return exactly this JSON structure:

{{
    "professional_title": "Professional title",
    "summary": "2 to 4 concise sentences",
    "skills": [
        "Skill 1",
        "Skill 2"
    ],
    "education": "Professionally formatted education",
    "experience": "Professionally rewritten experience",
    "projects": [
        "Professionally rewritten project description"
    ]
}}
"""

    response = client.chat.completions.create(
        model=CHAT_MODEL,

        temperature=0,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],

        response_format={
            "type": "json_object"
        },
    )

    content = (
        response
        .choices[0]
        .message
        .content
    )

    if not content:
        raise ValueError(
            "AI returned empty resume content."
        )

    try:
        result = json.loads(content)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "AI returned invalid JSON."
        ) from exc

    required_fields = {
        "professional_title",
        "summary",
        "skills",
        "education",
        "experience",
        "projects",
    }

    missing_fields = (
        required_fields -
        set(result.keys())
    )

    if missing_fields:
        raise ValueError(
            "AI response is missing fields: "
            + ", ".join(
                sorted(missing_fields)
            )
        )

    if not isinstance(
        result["skills"],
        list,
    ):
        raise ValueError(
            "AI skills must be a list."
        )

    if not isinstance(
        result["projects"],
        list,
    ):
        raise ValueError(
            "AI projects must be a list."
        )

    return result