from pathlib import Path

from fastapi import Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.conf.dburl import config
from src.services.auth_services import auth_service
from src.conf.dburl import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="TODO system",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
        Отправляет электронное сообщение для подтверждения адреса электронной почты пользователя.

        Parameters:
        - email: Адрес электронной почты пользователя.
        - username: Имя пользователя.
        - host: Хост, на котором запущено приложение.

        Raises:
        - ConnectionErrors: Возникает при ошибке подключения при отправке сообщения.

        Returns:
        Нет возвращаемого значения. Отправляет электронное сообщение для подтверждения адреса электронной почты.
        """
    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


fastmail = FastMail(conf)


async def send_password_email(email: str, token: str, host: str, password: str):
    """
        Отправляет электронное сообщение с новым паролем пользователю.

        Parameters:
        - email: Адрес электронной почты пользователя.
        - token: Токен для подтверждения сброса пароля.
        - host: Хост, на котором запущено приложение.
        - password: Новый сгенерированный пароль пользователя.

        Returns:
        Нет возвращаемого значения. Отправляет электронное сообщение с новым паролем пользователю.
        """
    token_verification = auth_service.create_email_token({"sub": email, "password": password})
    message = MessageSchema(
        subject="Ваш новый пароль",
        recipients=[email],
        template_body={'email': email, 'token': token, 'host': host, 'password': password,},
        subtype=MessageType.html
    )
    await fastmail.send_message(message, template_name="password.html")
