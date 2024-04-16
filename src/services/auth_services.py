from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from src.contacts.models import User
from src.db.connectdb import get_db
from src.repository import functionuser as repository_users
from src.conf.dburl import config


class Auth:
    """
        Класс для аутентификации и авторизации пользователей.

        Attributes:
        - pwd_context: Контекст шифрования паролей.
        - SECRET_KEY: Секретный ключ для создания токенов.
        - ALGORITHM: Алгоритм шифрования токенов.
        """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')
    SECRET_KEY = config.SECRET_KEY_JWT
    ALGORITHM = config.ALGORITHM

    def verify_password(self, plain_password, hashed_password):
        """Проверяет соответствие введенного пароля хэшу пароля в базе данных."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """Хэширует пароль."""
        return self.pwd_context.hash(password)

    auth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """Создает токен доступа."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire, 'scope': 'access_token'})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """Создает токен обновления."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """Декодирует токен обновления и возвращает электронную почту пользователя."""
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(auth2_scheme), db: AsyncSession = Depends(get_db)):
        """Получает текущего пользователя из токена."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}, )
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        return user

    async def create_email_token(self, data: dict):
        """Создает токен для подтверждения адреса электронной почты."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({'iat': datetime.utcnow(), 'exp': expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """Декодирует токен и возвращает адрес электронной почты."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='invalid token')

    async def create_password_token(self, email, password):
        """Создает токен для сброса пароля."""
        payload = {
            'password':password,
            'email': email,
            'exp': datetime.utcnow() + timedelta(days=1)  # Токен будет действителен 1 день
        }
        token = jwt.encode(payload, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def verify_password_reset_token(self, token):
        """Верифицирует токен сброса пароля."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload.get('password')
        except HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail='invalid token'):
            return None

    async def get_email_reset_token(self, token):
        """Возвращает адрес электронной почты из токена сброса пароля."""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload.get('email')
        except HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,detail='invalid token'):
            return None


auth_service = Auth()
