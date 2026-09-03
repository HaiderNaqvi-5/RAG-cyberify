from pydantic import BaseModel, Field


class SignatureUpload(BaseModel):
    filename: str = Field(
        min_length=1,
        max_length=300,
    )

    signature_data: str = Field(
        min_length=20,
    )


class SignatureResponse(BaseModel):
    success: bool
    signature_id: int
    filename: str
    size_bytes: int