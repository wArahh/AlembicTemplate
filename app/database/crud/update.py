from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Credentials


async def update_password(
        session: AsyncSession,
        credentials_name: str,
        new_password: str,
) -> None:
    """Update password of credentials"""
    statement = (
        update(Credentials)
        .where(Credentials.name == credentials_name)
        .values(password=new_password)
    )
    await session.execute(statement)
    await session.commit()
