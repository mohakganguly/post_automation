
import logging
from datetime import datetime, timezone
from urllib.parse import urlencode

from oauthlib.oauth1 import (
    Client as OAuth1Client,
    SIGNATURE_HMAC,
    SIGNATURE_TYPE_AUTH_HEADER,
)

from app.schemas import PlatformResult
from app.config import settings

logger = logging.getLogger(__name__)


class TumblrPlatform:

    name = "tumblr"

    def __init__(self, client):
        self.client = client
        self.blog_name = settings.tumblr_blog_name

        self.oauth = OAuth1Client(
            client_key=settings.tumblr_consumer_key,
            client_secret=settings.tumblr_consumer_secret,
            resource_owner_key=settings.tumblr_oauth_token,
            resource_owner_secret=settings.tumblr_oauth_token_secret,
            signature_method=SIGNATURE_HMAC,
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
        )

    async def publish(self, message: str) -> PlatformResult:

        # Legacy Tumblr text-post endpoint
        url = (
            f"https://api.tumblr.com/v2/blog/"
            f"{self.blog_name}/post"
        )

        payload = {
            "type": "text",
            "body": message,
            "state": "draft",
        }

        try:
            body = urlencode(payload)

            signed_uri, signed_headers, signed_body = (
                self.oauth.sign(
                    url,
                    http_method="POST",
                    body=body,
                    headers={
                        "Content-Type": (
                            "application/x-www-form-urlencoded"
                        ),
                        "User-Agent": "AutoPostAI/1.0",
                    },
                )
            )

            response = await self.client.post(
                signed_uri,
                content=signed_body,
                headers=signed_headers,
            )

            response.raise_for_status()

            result = response.json()

            if result.get("meta", {}).get("status") not in (200, 201):
                raise RuntimeError(
                    result.get("meta", {}).get(
                        "msg", "Tumblr API returned an error"
                    )
                )

            data = result.get("response", {})
            post_id = data.get("id")

            if not post_id:
                raise RuntimeError(
                    f"Tumblr did not return a post ID: {result}"
                )

            now = datetime.now(timezone.utc)

            return PlatformResult(
                platform=self.name,
                status="success",
                posted_url=(
                    f"https://{self.blog_name}/post/{post_id}"
                ),
                public_access=False,
                date=now.strftime("%Y-%m-%d"),
                time=now.strftime("%H:%M:%S"),
            )

        except Exception as exc:
            logger.exception("Tumblr publishing failed")

            return PlatformResult(
                platform=self.name,
                status="failed",
                error=str(exc),
            )

    def failure_result(self, error: str) -> PlatformResult:
        return PlatformResult(
            platform=self.name,
            status="failed",
            error=error,
        )
