def test_register_and_login_logout(client):
    # registration
    rv = client.post('/auth/register', data={
        'username':'testuser',
        'email':'test@example.com',
        'password':'Password123!',
        'password2':'Password123!'
    }, follow_redirects=True)
    assert b'Registration successful' in rv.data

    # login
    rv = client.post('/auth/login', data={
        'username':'testuser','password':'Password123!'
    }, follow_redirects=True)
    assert b'Logout' in rv.data

    # logout
    rv = client.get('/auth/logout', follow_redirects=True)
    assert b'Login' in rv.data

def test_password_reset_flow(client, app):
    # create a user
    client.post('/auth/register', data={
        'username':'pwuser','email':'pw@example.com',
        'password':'Secret123!','password2':'Secret123!'
    })
    # request reset
    rv = client.post('/auth/reset_password_request',
                     data={'email':'pw@example.com'},
                     follow_redirects=True)
    assert b'you will receive' in rv.data

    # grab token from DB
    with app.app_context():
        from app.models.user import User
        u = User.query.filter_by(email='pw@example.com').first()
        token = u.get_reset_password_token()

    # reset
    rv = client.post(f'/auth/reset_password/{token}',
                     data={'password':'Newpass123!','password2':'Newpass123!'},
                     follow_redirects=True)
    assert b'password has been reset' in rv.data

    # login with new password
    rv = client.post('/auth/login', data={
        'username':'pwuser','password':'Newpass123!'
    }, follow_redirects=True)
    assert b'Logout' in rv.data
