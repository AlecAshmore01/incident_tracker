import pytest

@pytest.fixture
def logged_in_client(client):
    # register & login a test admin
    client.post('/auth/register', data={
        'username':'admin','email':'admin@x.com',
        'password':'Admin123!','password2':'Admin123!'
    })
    # promote to admin
    from app.models.user import User
    with client.application.app_context():
        u = User.query.filter_by(username='admin').first()
        u.role = 'admin'; client.application.extensions['sqlalchemy'].db.session.commit()
    client.post('/auth/login', data={'username':'admin','password':'Admin123!'})
    return client

def test_create_read_update_delete_incident(logged_in_client):
    c = logged_in_client

    # create a category first
    c.post('/categories/create', data={'name':'TestCat','description':'d'})

    # create incident
    rv = c.post('/incidents/create', data={
        'title':'Test','description':'Desc','status':'Open','category':'1'
    }, follow_redirects=True)
    assert b'Incident created' in rv.data

    # list & view
    rv = c.get('/incidents/')
    assert b'Test' in rv.data
    rv = c.get('/incidents/1')
    assert b'Desc' in rv.data

    # edit
    rv = c.post('/incidents/1/edit', data={
        'title':'Test2','description':'Desc2','status':'Closed','category':'1'
    }, follow_redirects=True)
    assert b'Incident updated' in rv.data
    assert b'Test2' in rv.data

    # delete
    rv = c.post('/incidents/1/delete', follow_redirects=True)
    assert b'Incident deleted' in rv.data
    rv = c.get('/incidents/')
    assert b'Test2' not in rv.data
