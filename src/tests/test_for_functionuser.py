import unittest

from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.contacts.models import User, Contact
from src.schemas.user import UserSchema
from src.repository.functionuser import create_user, get_user_by_email, update_token, confirmed_email, update_password


class TestForUserFunctions(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = User(id=1, username='test user', password='123123', confirmed=False)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_create_user(self):
        body = UserSchema(username='bob', email='top@gmail.com', password='123123')
        result = await create_user(body, self.session)
        self.assertIsInstance(result, User)

    async def test_get_user_by_email(self):
        email = 'top@gmail.com'
        mocket_user = MagicMock()
        mocket_user.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mocket_user
        result = await get_user_by_email(email, self.session)
        self.assertIsInstance(result, User)

    async def test_update_token(self):
        new_token = '12sf3f'
        mocket_user = MagicMock()
        await update_token(self.user, new_token, self.session)
        assert self.user.refresh_token == new_token






