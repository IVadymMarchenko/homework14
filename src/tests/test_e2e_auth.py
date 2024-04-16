from unittest.mock import Mock
import pytest
from sqlalchemy import select

from conftest import TestingSessionLocal
from src.contacts.models import User

user_data = {"username": "agent007", "email": "agent0071@gmail.com", "password": "12345678"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
    response = client.post('auth/signup', json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data['username'] == user_data['username']
    assert data['email'] == user_data['email']
    assert mock_send_email.called


# def test_repeat_signup(client, monkeypatch):
#     mock_send_email = Mock()
#     monkeypatch.setattr('src.routes.auth.send_email', mock_send_email)
#     response = client.post('auth/signup', json=user_data)
#     assert response.status_code == 409, response.text
#     data = response.json()
#     assert data['detail'] == 'Account already exist'

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get('email')))
        current_user=current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed=True
            await session.commit()
    login_data = {'username': user_data['email'], 'password': user_data['password']}

    response = client.post('auth/login', data=login_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data



# def test_wrong_password_login(client):
#
#     response = client.post('/auth/login', data={'username':user_data.get('email'),'password':user_data.get('password')})
#     assert response.status_code == 401, response.text
#     data = response.json()
#     assert data["detail"] == 'invalid password'
