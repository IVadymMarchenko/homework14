import random
import string
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.db.connectdb import get_db
from src.contacts.models import User
from src.schemas.user import UserSchema
from src.contacts.models import User


async def create_user(body: UserSchema, db: AsyncSession):
    """
        Создает нового пользователя в базе данных.

        Parameters:
        - body: данные для создания нового пользователя (тип UserSchema).
        - db: сессия базы данных (тип AsyncSession).

        Returns:
        - созданный пользователь.
        """
    new_user = User(**body.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    """
        Получает пользователя из базы данных по его адресу электронной почты.

        Parameters:
        - email: адрес электронной почты пользователя (строка).
        - db: сессия базы данных (тип AsyncSession), по умолчанию получается с помощью функции get_db.

        Returns:
        - найденный пользователь или None, если пользователь не найден.
        """
    smt = select(User).filter_by(email=email)
    user = await db.execute(smt)
    user = user.scalar_one_or_none()
    return user


async def update_token(user: User, token: str | None, db: AsyncSession):
    """
        Обновляет токен обновления пользователя в базе данных.

        Parameters:
        - user: объект пользователя (тип User), для которого нужно обновить токен.
        - token: новый токен обновления (строка) или None, если нужно удалить текущий токен.
        - db: сессия базы данных (тип AsyncSession), через которую выполняется обновление.

        Returns:
        - None
        """
    user.refresh_token = token
    await db.commit()


async def confirmed_email(email: str, db: AsyncSession):
    """
        Подтверждает адрес электронной почты пользователя в базе данных.

        Parameters:
        - email: адрес электронной почты пользователя, которого нужно подтвердить.
        - db: сессия базы данных (тип AsyncSession), через которую выполняется обновление.

        Returns:
        - None
        """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    await db.commit()


async def update_avatar_url(email: str, url: str | None, db: AsyncSession) -> User:
    """
        Обновляет URL аватара пользователя в базе данных.

        Parameters:
        - email: адрес электронной почты пользователя, чей аватар нужно обновить.
        - url: новый URL аватара.
        - db: сессия базы данных (тип AsyncSession), через которую выполняется обновление.

        Returns:
        - Объект пользователя (тип User) с обновленным URL аватара.
        """
    user = await get_user_by_email(email, db)
    user.avatar = url
    await db.commit()
    await db.refresh(user)
    return user


# async def generate_password():
#     """
#         Генерирует случайный пароль.
#
#         Returns:
#         - Случайно сгенерированный пароль (тип str).
#         """
#     letters = string.ascii_letters + string.digits
#     new_password = ''.join(random.choice(letters) for i in range(6))
#     return new_password


async def update_password(email: str, password: str, db: AsyncSession) -> None:
    """
       Обновляет пароль пользователя.

       Parameters:
       - email: Электронная почта пользователя, чей пароль нужно обновить (тип str).
       - password: Новый пароль пользователя (тип str).
       - db: Сессия базы данных (тип AsyncSession).

       Returns:
       - None
       """
    user = await get_user_by_email(email, db)
    user.password = password
    await db.commit()
