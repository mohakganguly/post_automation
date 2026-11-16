
import re
from datetime import datetime, timezone
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class PostingRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Message containing exactly one CTA URL"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError("Message cannot be empty")

        # Extract URLs
        urls = re.findall(
            r"https?://[^\s<>]+",
            value
        )

        if len(urls) != 1:
            raise ValueError(
                "Message must contain exactly one URL"
            )

        url = urls[0].rstrip(".,!?;:)")

        parsed = urlparse(url)

        if (
            parsed.scheme not in ("http", "https")
            or not parsed.hostname
            or "." not in parsed.hostname
        ):
            raise ValueError("Invalid URL")

        # Reject malformed URL candidates
        if url != urls[0]:
            value = value.replace(urls[0], url)

        return value


class PlatformResult(BaseModel):

    platform: str

    status: Literal["success", "failed"]

    posted_url: str | None = None

    public_access: bool = False

    date: str | None = None

    time: str | None = None

    error: str | None = None


class PostingResponse(BaseModel):

    success: bool

    results: list[PlatformResult]
