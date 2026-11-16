
import asyncio
import httpx

from app.platforms.mastodon import MastodonPlatform
from app.platforms.bluesky import BlueskyPlatform
from app.platforms.devto import DevToPlatform
from app.platforms.telegram import TelegramPlatform
from app.platforms.tumblr import TumblrPlatform


async def main():

    message = (
        "Testing my automated multi-platform posting system. "
        "https://example.com"
    )

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True
    ) as client:

        platforms = [
            BlueskyPlatform(client),
            TelegramPlatform(client),
            MastodonPlatform(client),
            DevToPlatform(client),
            TumblrPlatform(client),
        ]

        for platform in platforms:

            print(f"\nPublishing to {platform.name}...")

            try:
                result = await platform.publish(message)

                print("Status:", result.status)
                print("URL:", result.posted_url)
                print("Public:", result.public_access)
                print("Error:", result.error)

            except Exception as exc:
                print("Unexpected error:", str(exc))


if __name__ == "__main__":
    asyncio.run(main())
