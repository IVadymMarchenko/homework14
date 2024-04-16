import cloudinary
import cloudinary.uploader
from sqlalchemy import select
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Depends, BackgroundTasks, Request
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.connectdb import get_db
from src.contacts.models import User
from src.schemas.user import UserResponse
from src.services.auth_services import auth_service
from src.conf.dburl import config
from fastapi import FastAPI, APIRouter, status
from src.repository import functionuser
from src.services.email_services import send_password_email
from src.schemas.user import PasswordForm

router = APIRouter()
cloudinary.config(cloud_name=config.CLD_NAME, api_key=config.CLD_API_KEY, api_secret=config.CLD_API_SECRET, secure=True)


@router.get('/me', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    """
        Получает текущего пользователя.

        Parameters:
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.

        Returns:
        - Информация о текущем пользователе (тип UserResponse).
        """
    return user


@router.patch('/avatar', response_model=UserResponse, dependencies=[Depends(RateLimiter(times=1, seconds=20))])
async def get_current_user(file: UploadFile = File(), user: User = Depends(auth_service.get_current_user),
                           db: AsyncSession = Depends(get_db)):
    """
        Обновляет аватар пользователя.

        Parameters:
        - file: Файл изображения аватара (тип UploadFile), передаваемый в теле запроса.
        - user: Текущий пользователь (тип User), получаемый из зависимости auth_service.get_current_user.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.

        Returns:
        - Информация о пользователе с обновленным аватаром (тип UserResponse).
        """
    public_id = f'Web16/{user.email}'
    res = cloudinary.uploader.upload(file.file, public_id=public_id, owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill',
                                                              version=res.get('version'))
    user = await functionuser.update_avatar_url(user.email, res_url, db)
    return user



@router.get('/reset-password/{token}')
async def new_password(token: str, db: AsyncSession = Depends(get_db)):
    """
        Устанавливает новый пароль для пользователя по токену сброса пароля.

        Parameters:
        - token: Токен сброса пароля (строка), передаваемый в качестве параметра пути.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.

        Returns:
        - Сообщение об успешном обновлении пароля (словарь).
        """
    email = await auth_service.get_email_reset_token(token)
    password = await auth_service.verify_password_reset_token(token)
    user = await functionuser.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if password:
        password = auth_service.get_password_hash(password)
        await functionuser.update_password(email, password, db)
    return {"message": "New password updated!"}


@router.post('/reset_password')
async def reset_password(body: PasswordForm, request: Request, db: AsyncSession = Depends(get_db)):
    """
        Сбрасывает пароль пользователя и отправляет письмо с подтверждением сброса пароля.

        Parameters:
        - body: Данные формы сброса пароля (тип PasswordForm).
        - request: Объект запроса FastAPI (тип Request), используется для получения базового URL.
        - db: Сессия базы данных (тип AsyncSession), получаемая из зависимости get_db.

        Returns:
        - Сообщение о том, что пароль отправлен на указанный email (словарь).
        """
    query = select(User).filter(User.email == body.email)
    result = await db.execute(query)
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь с таким email не найден"
        )

    token = await auth_service.create_password_token(body.email, body.password)

    await send_password_email(body.email,  token, str(request.base_url), body.password,)
    print(str(request.base_url))
    print(body.password)

    return {'message': 'password send to email'}

