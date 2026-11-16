
import asyncio
import httpx

from app.config import settings
from oauthlib.oauth1 import (
    Client as OAuth1Client,
    SIGNATURE_HMAC,
    SIGNATURE_TYPE_AUTH_HEADER,
)

async def check_credentials():

    async with httpx.AsyncClient(timeout=15.0) as client:

        # 1. Bluesky
        print("\nChecking Bluesky...")

        try:
            response = await client.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={
                    "identifier": settings.bluesky_handle,
                    "password": settings.bluesky_app_password
                }
            )

            if response.status_code == 200:
                print("Bluesky: AUTHENTICATED")
            else:
                print("Bluesky: FAILED", response.status_code,
                      response.text[:200])

        except Exception as exc:
            print("Bluesky: ERROR", str(exc))

        # 2. Telegram
        print("\nChecking Telegram...")

        try:
            url = (
                "https://api.telegram.org/bot"
                f"{settings.telegram_bot_token}/getMe"
            )

            response = await client.get(url)

            if response.status_code == 200 and response.json().get("ok"):
                bot = response.json()["result"]
                print("Telegram: AUTHENTICATED")
                print("Bot username:", bot.get("username"))
            else:
                print("Telegram: FAILED", response.text[:200])

        except Exception as exc:
            print("Telegram: ERROR", str(exc))

        # 3. Mastodon
        print("\nChecking Mastodon...")

        try:
            url = (
                settings.mastodon_base_url.rstrip("/")
                + "/api/v1/accounts/verify_credentials"
            )

            response = await client.get(
                url,
                headers={
                    "Authorization": (
                        f"Bearer {settings.mastodon_access_token}"
                    )
                }
            )

            if response.status_code == 200:
                print("Mastodon: AUTHENTICATED")
                print("Username:", response.json().get("username"))
            else:
                print("Mastodon: FAILED", response.status_code,
                      response.text[:200])

        except Exception as exc:
            print("Mastodon: ERROR", str(exc))

        # 4. DEV Community
        print("\nChecking DEV Community...")

        try:
            response = await client.get(
                "https://dev.to/api/users/me",
                headers={
                    "api-key": settings.dev_api_key,
                    "Accept": "application/vnd.forem.api-v1+json"
                }
            )

            if response.status_code == 200:
                print("DEV: AUTHENTICATED")
                print("Username:", response.json().get("username"))
            else:
                print("DEV: FAILED", response.status_code,
                      response.text[:200])

        except Exception as exc:
            print("DEV: ERROR", str(exc))


        # 5. Tumblr
        print("\nChecking Tumblr...")

        try:
            oauth = OAuth1Client(
                client_key=settings.tumblr_consumer_key,
                client_secret=settings.tumblr_consumer_secret,
                resource_owner_key=settings.tumblr_oauth_token,
                resource_owner_secret=settings.tumblr_oauth_token_secret,
                signature_method=SIGNATURE_HMAC,
                signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            )

            url = (
                f"https://api.tumblr.com/v2/blog/"
                f"{settings.tumblr_blog_name}/info"
            )

            signed_uri, signed_headers, _ = oauth.sign(
                url,
                http_method="GET",
            )

            response = await client.get(
                signed_uri,
                headers=signed_headers,
            )

            if response.status_code == 200:
                data = response.json()["response"]["blog"]

                print("Tumblr: AUTHENTICATED")
                print("Blog name:", data.get("name"))
                print("Blog title:", data.get("title"))

            else:
                print(
                    "Tumblr: FAILED",
                    response.status_code,
                    response.text[:200],
                )

        except Exception as exc:
            print("Tumblr: ERROR", str(exc))


if __name__ == "__main__":
    asyncio.run(check_credentials())
