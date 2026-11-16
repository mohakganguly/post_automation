
from app.platforms.base import BasePlatform
from app.config import settings


class DevToPlatform(BasePlatform):

    @property
    def name(self):
        return "DEV Community"

    async def publish(self, message: str):

        if not settings.dev_api_key:
            return self.failure_result(
                "DEV API key not configured"
            )

        try:
            response = await self.client.post(
                "https://dev.to/api/articles",
                headers={
                    "api-key": settings.dev_api_key
                },
                json={
                    "article": {
                        "title": "A Quick Update",
                        "body_markdown": message,
                        "published": True
                    }
                }
            )

            response.raise_for_status()
            data = response.json()

            posted_url = data.get("url")

            if not posted_url:
                return self.failure_result(
                    "DEV did not return an article URL"
                )

            return self.success_result(
                posted_url=posted_url,
                public_access=True
            )

        except Exception as exc:
            return self.failure_result(str(exc))
