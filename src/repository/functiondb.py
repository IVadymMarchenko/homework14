import sys

from sqlalchemy import select, cast, Date, or_, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from src.contacts.models import Contact, User
from src.schemas.checkschemas import CreateContactSchema, CreateContact
from datetime import datetime, timedelta
from sqlalchemy import func

async def get_contacts(limit: int, offset: int, db: AsyncSession,user: User):
    """
        Получает контакты из базы данных для указанного пользователя.

        Parameters:
        - limit (int): Максимальное количество контактов для извлечения.
        - offset (int): Смещение для запроса (начиная с какого индекса извлекать контакты).
        - db (AsyncSession): Сессия базы данных.
        - user (User): Пользователь, для которого нужно получить контакты.

        Returns:
        - List[Contact]: Список контактов для указанного пользователя.
        """
    smt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(smt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession,user: User):
    """
        Получает контакт из базы данных по его идентификатору для указанного пользователя.

        Parameters:
        - contact_id (int): Идентификатор контакта.
        - db (AsyncSession): Сессия базы данных.
        - user (User): Пользователь, для которого нужно получить контакт.

        Returns:
        - Optional[Contact]: Контакт с указанным идентификатором для указанного пользователя.
          Возвращает None, если контакт не найден.
        """
    smt = select(Contact).filter_by(id=contact_id,user=user)
    contact = await db.execute(smt)
    return contact.scalar_one_or_none()


async def create_contact(body: CreateContactSchema, db: AsyncSession, user: User):
    """
        Создает новый контакт в базе данных для указанного пользователя.

        Parameters:
        - body (CreateContactSchema): Данные для создания нового контакта.
        - db (AsyncSession): Сессия базы данных.
        - user (User): Пользователь, для которого создается контакт.

        Returns:
        - Contact: Новый созданный контакт.
        """
    contact = Contact(**body.model_dump(exclude_unset=True),user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: CreateContactSchema, db: AsyncSession,user: User):
    """
        Обновляет информацию о контакте в базе данных.

        Parameters:
        - contact_id (int): Идентификатор контакта, который требуется обновить.
        - body (CreateContactSchema): Новые данные для обновления контакта.
        - db (AsyncSession): Сессия базы данных.
        - user (User): Пользователь, чей контакт требуется обновить.

        Returns:
        - Contact: Обновленный контакт. Если контакт не найден, возвращает None.
        """
    smt = select(Contact).filter_by(id=contact_id,user=user)
    contacts = await db.execute(smt)
    contact = contacts.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.phone = body.phone
        contact.email = body.email
        contact.birthday = body.birthday
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    """
       Удаляет контакт из базы данных.

       Parameters:
       - contact_id (int): Идентификатор контакта, который требуется удалить.
       - db (AsyncSession): Сессия базы данных.

       Returns:
       - Contact: Удаленный контакт. Если контакт не найден, возвращает None.
       """
    smt = select(Contact).filter_by(id=contact_id)
    contacts = await db.execute(smt)
    contact = contacts.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def upcoming_birthday(db: AsyncSession):
    """
        Возвращает список контактов, у которых день рождения наступит в течение следующих 7 дней.

        Parameters:
        - db (AsyncSession): Сессия базы данных.

        Returns:
        - List[Contact]: Список контактов, у которых день рождения наступит в течение следующих 7 дней.
        """
    today = datetime.today().date()
    week_from_now = today + timedelta(days=3)

    # Запит до бази даних для отримання контактів з днями народження у межах наступних 7 днів
    stmt = select(Contact).filter(
        or_(
            and_(
                extract('month', Contact.birthday) == today.month,
                extract('day', Contact.birthday) >= today.day
            ),
            and_(
                extract('month', Contact.birthday) == week_from_now.month,
                extract('day', Contact.birthday) <= week_from_now.day
            ),
            and_(
                extract('month', Contact.birthday) == (today.month + 1) % 12,
                extract('day', Contact.birthday) <= week_from_now.day
            )
        )
    )

    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def look_for_contact(db: AsyncSession, name_contact: str):
    """
        Ищет контакт в базе данных по имени, фамилии или электронной почте.

        Parameters:
        - db (AsyncSession): Сессия базы данных.
        - name_contact (str): Имя, фамилия или адрес электронной почты контакта.

        Returns:
        - Optional[Contact]: Найденный контакт или None, если контакт не найден.
        """
    query = select(Contact).filter(or_(Contact.name == name_contact,
                                       Contact.surname == name_contact,
                                       Contact.email == name_contact))
    result = await db.execute(query)
    contact = result.scalar_one_or_none()
    return contact
