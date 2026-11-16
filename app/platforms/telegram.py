
from app.platforms.base import BasePlatform
from app.config import settings


class TelegramPlatform(BasePlatform):

    @property
    def name(self):
        return "Telegram"

    async def publish(self, message: str):

        if not all([
            settings.telegram_bot_token,
            settings.telegram_channel_id
        ]):
            return self.failure_result(
                "Telegram credentials not configured"
            )

        try:
            api_url = (
                "https://api.telegram.org/bot"
                f"{settings.telegram_bot_token}/sendMessage"
            )

            response = await self.client.post(
                api_url,
                json={
                    "chat_id": settings.telegram_channel_id,
                    "text": message,
                    "link_preview_options": {
                        "is_disabled": False
                    }
                }
            )

            response.raise_for_status()
            data = response.json()

            if not data.get("ok"):
                return self.failure_result(
                    data.get("description", "Telegram API error")
                )

            result = data["result"]
            message_id = result["message_id"]

            # Public channel usernames begin with @
            channel = settings.telegram_channel_id

            if channel.startswith("@"):
                username = channel[1:]
                posted_url = (
                    f"https://t.me/{username}/{message_id}"
                )
                public_access = True
            else:
                posted_url = None
                public_access = False

            return self.success_result(
                posted_url=posted_url,
                public_access=public_access
            )

        except Exception as exc:
            return self.failure_result(str(exc))
