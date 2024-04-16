import unittest
from unittest.mock import MagicMock, AsyncMock
from src.repository.functiondb import get_contacts, get_contact, create_contact, update_contact, delete_contact, \
    upcoming_birthday, look_for_contact
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.checkschemas import CreateContactSchema, CreateContact
from src.contacts.models import User, Contact
import datetime
from datetime import datetime, timedelta


class TestAsyncForDB(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.user = User(id=1, username='test user', password='123123', confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, name='Jack', surname='Bol', phone='30983332211', email='top@gmail.com', user=self.user),
            Contact(id=1, name='John', surname='Boll', phone='30983332244', email='top2@gmail.com', user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contacts = [
            Contact(id=contact_id, name='Jack', surname='Bol', phone='30983332211', email='top@gmail.com',
                    user=self.user)]
        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_create_contact(self):
        new_contact = Contact(name='Bob', surname='Bill', phone='300962223344', email='qwer@gmail.com',
                              birthday='1992-01-01', information='dsff')

        body = CreateContactSchema(name='Bob', surname='Bill', phone='300962223344', email='qwer@gmail.com',
                                   birthday='1992-01-01', information='dsff')
        result = await create_contact(body, self.session, self.user)
        self.assertIsInstance(result, Contact)
        self.assertEqual(result.name, new_contact.name)
        self.assertEqual(result.surname, new_contact.surname)
        self.assertEqual(result.phone, new_contact.phone)
        self.assertEqual(result.email, new_contact.email)
        self.assertEqual(result.information, new_contact.information)

    async def test_update_contact(self):
        updated_contact = Contact(name='Bob', surname='Bill', phone='300962223344', email='qwer@gmail.com',
                                  birthday='1992-01-01', information='dsff')

        body = CreateContactSchema(name='Bob', surname='Bill', phone='300962223344', email='qwer@gmail.com',
                                   birthday='1992-01-01', information='dsff')

        mocked_contacts = MagicMock()
        mocked_contacts.scalar_one_or_none.return_value = updated_contact
        self.session.execute.return_value = mocked_contacts

        result = await update_contact(1, body, self.session, self.user)

        self.assertEqual(result, updated_contact)

    async def test_delete_contact(self):
        mocket_contacts = MagicMock()
        mocket_contacts.scalar_one_or_none.return_value = Contact(name='Bob', surname='Bill', phone='300962223344',
                                                                  email='qwer@gmail.com',
                                                                  birthday='1992-01-01', information='dsff')
        self.session.execute.return_value = mocket_contacts
        result = await delete_contact(1, self.session)
        self.assertIsInstance(result, Contact)

    async def test_upcoming_birthday(self):
        today = datetime.today().date()
        week_from_now = today + timedelta(days=7)
        contacts = [
            Contact(name='Alice', birthday=today),
            Contact(name='Bob', birthday=week_from_now),
            Contact(name='Charlie', birthday=(
                today.replace(year=today.year + 1) if today.month == 12 else today.replace(month=today.month + 1)))
        ]
        mocket_contacts = MagicMock()
        mocket_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocket_contacts
        result = await upcoming_birthday(self.session)
        for contact in result:
            self.assertIsInstance(contact, Contact)




