
import asyncio
import logging

from app.schemas import PostingResponse, PlatformResult

from app.platforms.mastodon import MastodonPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.tumblr import TumblrPlatform

logger = logging.getLogger(__name__)


class PostingService:

    def __init__(self, client):
        self.client = client

        self.platforms = [
            MastodonPlatform(client),
            BlueskyPlatform(client),
            DevToPlatform(client),
            TelegramPlatform(client),
            TumblrPlatform(client),
        ]

    async def _publish_safely(
        self,
        platform,
        message: str
    ) -> PlatformResult:

        try:
            return await platform.publish(message)

        except Exception as exc:
            logger.exception(
                "Unexpected error while posting to %s",
                platform.name
            )

            return platform.failure_result(
                f"Unexpected error: {str(exc)}"
            )

    async def publish_all(
        self,
        message: str
    ) -> PostingResponse:

        tasks = [
            self._publish_safely(platform, message)
            for platform in self.platforms
        ]

        results = await asyncio.gather(*tasks)

        overall_success = any(
            result.status == "success"
            for result in results
        )

        return PostingResponse(
            success=overall_success,
            results=results
        )
