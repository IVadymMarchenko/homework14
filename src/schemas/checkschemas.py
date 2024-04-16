from typing import Optional
from datetime import date
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, String, Integer, Date

from src.schemas.user import UserResponse


class CreateContactSchema(BaseModel):
    """
        Схема для создания нового контакта.

        Attributes:
        - name (str): Имя контакта, максимальная длина 30 символов.
        - surname (str): Фамилия контакта, максимальная длина 30 символов.
        - phone (str): Номер телефона контакта, максимальная длина 30 символов.
        - email (str): Адрес электронной почты контакта, максимальная длина 30 символов.
        - birthday (date): День рождения контакта.
        - information (Optional[str]): Дополнительная информация о контакте, максимальная длина 250 символов.
        """
    name: str = Field(max_length=30)
    surname: str = Field(max_length=30)
    phone: str = Field(max_length=(30))
    email: str = Field(max_length=30)
    birthday: date
    information: Optional[str] = Field(None, max_length=250)



class CreateContact(BaseModel):
    """
        Модель для созданного контакта.

        Attributes:
        - id (int): Уникальный идентификатор контакта.
        - name (str): Имя контакта.
        - surname (str): Фамилия контакта.
        - phone (str): Номер телефона контакта.
        - email (str): Адрес электронной почты контакта.
        - birthday (date): День рождения контакта.
        - information (str): Дополнительная информация о контакте.
        - user (Optional[UserResponse]): Пользователь, связанный с контактом (если есть).
        """
    id: int = 1
    name: str
    surname: str
    phone: str
    email: str
    birthday: date
    information: str
    user: UserResponse | None

    class Config:
        from_attributes = True
