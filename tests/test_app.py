import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app


# ---------- Fixtures ---------- #
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ---------- Tests ---------- #

def test_login_page_loads(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_invalid_credentials(client):
    response = client.post('/', data={'username': 'wrong', 'password': 'wrong'})
    assert b'Invalid credentials' in response.data

def test_login_valid_credentials(client):
    response = client.post('/', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome' in response.data or b'Library' in response.data

def test_search_title_requires_login(client):
    response = client.get('/search/title?title=test')
    assert response.status_code == 302  # redirected to login

def test_search_title_authenticated(client):
    client.post('/', data={'username': 'admin', 'password': 'password'})
    response = client.get('/search/title?title=Manual')
    assert b'Document' in response.data or response.status_code == 200

def test_upload_requires_login(client):
    response = client.get('/upload/manage')
    assert response.status_code == 302  # redirect

def test_upload_manage_authenticated(client):
    client.post('/', data={'username': 'admin', 'password': 'password'})
    response = client.get('/upload/manage')
    assert response.status_code == 200
    assert b'Manage' in response.data

def test_logout(client):
    client.post('/', data={'username': 'admin', 'password': 'password'})
    response = client.get('/logout', follow_redirects=True)
    assert b'Login' in response.data
