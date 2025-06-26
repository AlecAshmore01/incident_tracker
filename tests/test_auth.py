import pytest
from app.models.user import User

def test_registration_and_login(client):
    # Registration should redirect to login
    r1 = client.post('/auth/register', data={
        'username':'alice','email':'alice@example.com',
        'password':'Pass123!','confirm':'Pass123!'
    }, follow_redirects=False)
    assert r1.status_code == 302
    assert '/auth/login' in r1.headers['Location']

    # Duplicate registration stays on register page
    r2 = client.post('/auth/register', data={
        'username':'alice','email':'alice2@example.com',
        'password':'Pass123!','confirm':'Pass123!'
    }, follow_redirects=False)
    assert r2.status_code in (200, 400)

    # Wrong login
    r3 = client.post('/auth/login', data={
        'username':'alice','password':'wrong'
    }, follow_redirects=False)
    assert r3.status_code == 200

    # Correct login
    r4 = client.post('/auth/login', data={
        'username':'alice','password':'Pass123!'
    }, follow_redirects=False)
    assert r4.status_code == 302
    assert '/incidents/' in r4.headers['Location']

def test_password_reset_flow(client):
    # Register
    client.post('/auth/register', data={
        'username':'bob','email':'bob@example.com',
        'password':'Pass123!','confirm':'Pass123!'
    }, follow_redirects=True)

    # Request reset
    r1 = client.post('/auth/reset_password_request',
                     data={'email':'bob@example.com'},
                     follow_redirects=False)
    assert r1.status_code == 302

    # Generate token
    from app.models.user import User
    with client.application.app_context():
        u = User.query.filter_by(email='bob@example.com').first()
        token = u.get_reset_password_token()

    # Use token
    r2 = client.post(f'/auth/reset_password/{token}', data={
        'password':'Newpass1!','confirm':'Newpass1!'
    }, follow_redirects=False)
    assert r2.status_code == 302

    # Invalid token
    r3 = client.get('/auth/reset_password/invalid', follow_redirects=False)
    assert r3.status_code == 302
