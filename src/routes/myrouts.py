from fastapi import APIRouter, HTTPException, Query, Depends, status, Query
from datetime import datetime, timedelta
from fastapi_limiter.depends import RateLimiter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.auth_services import auth_service
from src.contacts.models import Contact, User
from src.db.connectdb import get_db
from src.repository import functiondb
from src.repository import functiondb
from src.schemas.checkschemas import CreateContactSchema, CreateContact

routs = APIRouter(prefix='/contacts', tags=['contacts'])


@routs.get('/', response_model=list[CreateContact])
async def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                       db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
        Получает список контактов.

        Parameters:
        - limit: Максимальное количество контактов для возврата (по умолчанию 10, минимум 10, максимум 100).
        - offset: Смещение для запроса списка контактов (по умолчанию 0, минимум 0).
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Список контактов (тип list[CreateContact]).
        """
    contacts = await functiondb.get_contacts(limit, offset, db, user)
    return contacts


@routs.get('/{contact_id}', response_model=CreateContactSchema)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                      user: User = Depends(auth_service.get_current_user)):
    """
        Получает информацию о контакте по его идентификатору.

        Parameters:
        - contact_id: Идентификатор контакта.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Информация о контакте (тип CreateContactSchema).
        """
    contact = await functiondb.get_contact(contact_id, db, user)
    return contact


@routs.post('/', response_model=CreateContact, status_code=status.HTTP_201_CREATED,
            dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def create_contact(body: CreateContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Создает новый контакт.

        Parameters:
        - body: Данные для создания нового контакта (тип CreateContactSchema).
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Созданный контакт (тип CreateContact).
        """
    contact = await functiondb.create_contact(body, db, user)
    return contact


@routs.put('/{contact_id}')
async def update_contact(contact_id: int, body: CreateContactSchema, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Обновляет данные о контакте.

        Parameters:
        - contact_id: Идентификатор контакта, который нужно обновить.
        - body: Новые данные контакта (тип CreateContactSchema).
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Обновленные данные о контакте (тип CreateContact).
        """
    contact = await functiondb.update_contact(contact_id, body, db, )
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return contact


@routs.delete('/{contact_id}')
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db),
                         user: User = Depends(auth_service.get_current_user)):
    """
        Удаляет контакт по его идентификатору.

        Parameters:
        - contact_id: Идентификатор контакта, который нужно удалить.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Удаленный контакт, если успешно; в противном случае - None.
        """
    contact = await functiondb.delete_contact(contact_id, db)
    return contact


@routs.get("/birthdays/", response_model=list[CreateContact])
async def get_birthdays(db: AsyncSession = Depends(get_db), user: User = Depends(auth_service.get_current_user)):
    """
        Получает список контактов, у которых день рождения наступает в течение следующих 7 дней.

        Parameters:
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Список контактов, у которых день рождения наступает в течение следующих 7 дней.
        """
    return await functiondb.upcoming_birthday(db)


@routs.get('/search_contact/{name_contact_or_surname_or_email}', response_model=CreateContactSchema)
async def look_for_contact(name_contact: str, db: AsyncSession = Depends(get_db),
                           user: User = Depends(auth_service.get_current_user)):
    """
        Ищет контакт по имени, фамилии или электронной почте.

        Parameters:
        - name_contact: Строка, содержащая имя, фамилию или электронную почту контакта.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.

        Returns:
        - Найденный контакт с указанным именем, фамилией или электронной почтой.
        """
    contact = await functiondb.look_for_contact(db, name_contact, user)
    return contact
