
import re
from datetime import datetime, timezone

from app.platforms.base import BasePlatform
from app.config import settings


class BlueskyPlatform(BasePlatform):

    @property
    def name(self):
        return "Bluesky"

    async def publish(self, message: str):

        if not all([
            settings.bluesky_handle,
            settings.bluesky_app_password
        ]):
            return self.failure_result(
                "Bluesky credentials not configured"
            )

        try:
            # Step 1: Authenticate
            auth_response = await self.client.post(
                "https://bsky.social/xrpc/com.atproto.server.createSession",
                json={
                    "identifier": settings.bluesky_handle,
                    "password": settings.bluesky_app_password
                }
            )

            auth_response.raise_for_status()
            session = auth_response.json()

            access_token = session["accessJwt"]
            did = session["did"]

            # Step 2: Create clickable URL facet
            url_match = re.search(
                r"https?://[^\s<>]+",
                message
            )

            record = {
                "$type": "app.bsky.feed.post",
                "text": message,
                "createdAt": datetime.now(
                    timezone.utc
                ).isoformat().replace("+00:00", "Z")
            }

            if url_match:
                url = url_match.group().rstrip(".,!?;:)")
                start = len(
                    message[:url_match.start()].encode("utf-8")
                )
                end = start + len(url.encode("utf-8"))

                record["facets"] = [{
                    "index": {
                        "byteStart": start,
                        "byteEnd": end
                    },
                    "features": [{
                        "$type": "app.bsky.richtext.facet#link",
                        "uri": url
                    }]
                }]

            # Step 3: Publish record
            response = await self.client.post(
                "https://bsky.social/xrpc/com.atproto.repo.createRecord",
                headers={
                    "Authorization": f"Bearer {access_token}"
                },
                json={
                    "repo": did,
                    "collection": "app.bsky.feed.post",
                    "record": record
                }
            )

            response.raise_for_status()
            data = response.json()

            uri = data.get("uri", "")
            rkey = uri.rsplit("/", 1)[-1]

            if not rkey:
                return self.failure_result(
                    "Bluesky did not return a record key"
                )

            posted_url = (
                f"https://bsky.app/profile/"
                f"{settings.bluesky_handle}/post/{rkey}"
            )

            return self.success_result(
                posted_url=posted_url,
                public_access=True
            )

        except Exception as exc:
            return self.failure_result(str(exc))
