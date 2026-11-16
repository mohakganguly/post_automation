
from app.platforms.base import BasePlatform
from app.config import settings


class MastodonPlatform(BasePlatform):

    @property
    def name(self):
        return "Mastodon"

    async def publish(self, message: str):

        if not all([
            settings.mastodon_base_url,
            settings.mastodon_access_token
        ]):
            return self.failure_result(
                "Mastodon credentials not configured"
            )

        try:
            base_url = settings.mastodon_base_url.rstrip("/")

            response = await self.client.post(
                f"{base_url}/api/v1/statuses",
                headers={
                    "Authorization": (
                        f"Bearer {settings.mastodon_access_token}"
                    )
                },
                data={
                    "status": message,
                    "visibility": "public"
                }
            )

            response.raise_for_status()
            data = response.json()

            posted_url = data.get("url")

            if not posted_url:
                return self.failure_result(
                    "Mastodon did not return a post URL"
                )

            return self.success_result(
                posted_url=posted_url,
                public_access=data.get("visibility") == "public"
            )

        except Exception as exc:
            return self.failure_result(str(exc))
