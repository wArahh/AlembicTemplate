from app import app_instance_logger
from app.database.crud.get import check_user_admin
from app.database.engine import AsyncSessionLocal


async def supercalifragilisticexpialidocious_func():
    app_instance_logger.info("hi there!")
    async with AsyncSessionLocal() as db_session:
        user_is_admin = await check_user_admin(
            user_id=1,
            db_session=db_session,
        )
        return user_is_admin
