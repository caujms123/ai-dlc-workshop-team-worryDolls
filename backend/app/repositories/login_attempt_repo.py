"""로그인 시도 리포지토리."""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.login_attempt import LoginAttempt


class LoginAttemptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_identifier(self, identifier: str) -> LoginAttempt | None:
        result = await self.session.execute(
            select(LoginAttempt).where(LoginAttempt.identifier == identifier)
        )
        return result.scalar_one_or_none()

    async def create_or_increment(self, identifier: str) -> LoginAttempt:
        attempt = await self.get_by_identifier(identifier)
        if attempt is None:
            attempt = LoginAttempt(
                identifier=identifier,
                attempt_count=1,
                last_attempt_at=datetime.now(timezone.utc),
            )
            self.session.add(attempt)
        else:
            attempt.attempt_count += 1
            attempt.last_attempt_at = datetime.now(timezone.utc)
        await self.session.flush()
        await self.session.refresh(attempt)
        return attempt

    async def reset(self, identifier: str) -> None:
        attempt = await self.get_by_identifier(identifier)
        if attempt:
            attempt.attempt_count = 0
            attempt.locked_until = None
            await self.session.flush()

    async def lock(self, identifier: str, locked_until: datetime) -> None:
        attempt = await self.get_by_identifier(identifier)
        if attempt:
            attempt.locked_until = locked_until
            await self.session.flush()
