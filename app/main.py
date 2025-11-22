from app import app_logger
from app.database.crud.get import check_user_admin
from app.database.engine import AsyncSessionLocal
from app.services.i18n import i18n


async def supercalifragilisticexpialidocious_func():
    print(i18n.user.message.welcome_message())
    app_logger.info(i18n.logs.bot.bot_logger_works())
    async with AsyncSessionLocal() as db_session:
        user_is_admin = await check_user_admin(
            user_id=1,
            db_session=db_session,
        )
        return user_is_admin
