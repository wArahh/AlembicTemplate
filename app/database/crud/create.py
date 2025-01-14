from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Credentials

async def create_credentials(
        session: AsyncSession,
        credentials_name: str,
        credentials_password: str,
) -> None:
    """Create credentials object"""
    credentials = Credentials(
        name=credentials_name,
        password=credentials_password,
    )
    session.add(credentials)
    await session.commit()
