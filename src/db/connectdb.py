import contextlib

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.conf.dburl import config


class ManageSession:
    """
        Класс для управления сессиями базы данных.
        """
    def __init__(self,url):
        """
                Инициализация объекта управления сессиями базы данных.

                Parameters:
                - url: URL для подключения к базе данных.
                """
        self._engine=create_async_engine(url)
        self._session_maker= async_sessionmaker(autoflush=False,autocommit=False,bind=self._engine)

    @contextlib.asynccontextmanager
    async def session(self):
        """
                Менеджер контекста для получения сессии базы данных.

                Yields:
                - Сессия базы данных.
                """
        if self._session_maker is None:
            raise Exception('No connect to DB')
        session=self._session_maker()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

session_manage=ManageSession(config.DB_URL)

async def get_db():
    """
        Функция для получения асинхронной сессии базы данных.

        Yields:
        - Асинхронная сессия базы данных.
    """
    async with session_manage.session() as session:
        yield session








# async def get_db():
#     engine = create_async_engine(config.DB_URL)
#     DBSession = async_sessionmaker(bind=engine)
#     async with DBSession() as session:
#         yield session
