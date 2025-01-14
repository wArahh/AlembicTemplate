from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Credentials


async def get_credentials(
        session: AsyncSession,
        credentials_name: str
) -> Sequence[Credentials] | None:
    """Getting certain credentials"""
    statement = select(Credentials).where(Credentials.name == credentials_name)
    return (
        await session.execute(statement)
    ).scalar_one_or_none()
