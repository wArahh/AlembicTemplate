from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Admin


async def check_user_admin(
        user_id: int,
        db_session: AsyncSession,
) -> bool:
    """
    :param db_session: async session.
    :param user_id: id of user.

    :return: True if admin, else False.
    """
    statement = select(
        exists()
    ).where(
        Admin.user_id == user_id
    )
    print(statement)
    result = await db_session.execute(statement)
    return result.scalar()
