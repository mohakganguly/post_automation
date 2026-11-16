
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import httpx

from app.schemas import PlatformResult


class BasePlatform(ABC):

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def publish(self, message: str) -> PlatformResult:
        pass

    def success_result(
        self,
        posted_url: str | None,
        public_access: bool = False
    ) -> PlatformResult:

        now = datetime.now(timezone.utc)

        return PlatformResult(
            platform=self.name,
            status="success",
            posted_url=posted_url,
            public_access=public_access,
            date=now.date().isoformat(),
            time=now.time().replace(microsecond=0).isoformat(),
            error=None
        )

    def failure_result(self, error: str) -> PlatformResult:

        return PlatformResult(
            platform=self.name,
            status="failed",
            posted_url=None,
            public_access=False,
            date=None,
            time=None,
            error=error
        )
