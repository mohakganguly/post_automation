
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import PostingService


@asynccontextmanager
async def lifespan(app: FastAPI):

    # One shared asynchronous HTTP client
    async with httpx.AsyncClient(
        timeout=httpx.Timeout(25.0, connect=10.0),
        follow_redirects=True
    ) as client:

        app.state.http_client = client
        yield


app = FastAPI(
    title="Automated Multi-Platform Posting API",
    description=(
        "Automatically publish messages across "
        "Reddit, Mastodon, Bluesky, DEV and Telegram."
    ),
    version="1.0.0",
    lifespan=lifespan
)


@app.post(
    "/posting",
    response_model=PostingResponse,
    summary="Publish message across five platforms"
)
async def create_post(request: PostingRequest):

    service = PostingService(
        app.state.http_client
    )

    result = await service.publish_all(
        request.message
    )

    return result


@app.get("/")
async def root():

    return {
        "message": "Automated Posting API is running",
        "endpoint": "/posting",
        "documentation": "/docs"
    }
