
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Tumblr - OAuth 1.0a
    tumblr_consumer_key: str = ""
    tumblr_consumer_secret: str = ""
    tumblr_oauth_token: str = ""
    tumblr_oauth_token_secret: str = ""
    tumblr_redirect_uri: str = ""
    tumblr_blog_name: str = ""

    # Mastodon
    mastodon_base_url: str = ""
    mastodon_access_token: str = ""

    # Bluesky
    bluesky_handle: str = ""
    bluesky_app_password: str = ""

    # DEV Community
    dev_api_key: str = ""

    # Telegram
    telegram_bot_token: str = ""
    telegram_channel_id: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
