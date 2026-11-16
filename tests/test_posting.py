
import pytest
from pydantic import ValidationError

from app.schemas import PostingRequest


def test_valid_message():
    request = PostingRequest(
        message="Check our platform https://example.com"
    )
    assert request.message == "Check our platform https://example.com"


def test_message_without_url():
    with pytest.raises(ValidationError):
        PostingRequest(message="Hello world")


def test_message_with_two_urls():
    with pytest.raises(ValidationError):
        PostingRequest(
            message="Visit https://example.com and https://google.com"
        )


def test_message_exceeds_200_characters():
    message = "A" * 190 + " https://example.com"

    with pytest.raises(ValidationError):
        PostingRequest(message=message)


def test_empty_message():
    with pytest.raises(ValidationError):
        PostingRequest(message="")


def test_whitespace_only_message():
    with pytest.raises(ValidationError):
        PostingRequest(message="   ")


def test_invalid_url():
    with pytest.raises(ValidationError):
        PostingRequest(message="Visit https://")


def test_url_without_protocol():
    with pytest.raises(ValidationError):
        PostingRequest(message="Visit example.com")


def test_http_url():
    request = PostingRequest(
        message="Visit http://example.com"
    )
    assert "http://example.com" in request.message


def test_message_with_trailing_punctuation():
    request = PostingRequest(
        message="Visit https://example.com."
    )
    assert request.message == "Visit https://example.com"

def test_message_with_query_parameters():
    request = PostingRequest(
        message="Visit https://example.com/page?id=10"
    )
    assert "id=10" in request.message


def test_missing_message():
    with pytest.raises(ValidationError):
        PostingRequest()


def test_message_wrong_type():
    with pytest.raises(ValidationError):
        PostingRequest(message=123)
