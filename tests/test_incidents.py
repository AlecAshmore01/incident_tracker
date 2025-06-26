import pytest
from app.models.incident import Incident
from app.models.category import IncidentCategory

@pytest.fixture
def sample_category(auth_client):
    # create a category via the route
    resp = auth_client.post('/categories/create', data={
        'name':'Network','description':'Net issues'
    }, follow_redirects=False)
    assert resp.status_code == 302
    return IncidentCategory.query.filter_by(name='Network').first()

def test_incident_crud(auth_client, sample_category):
    # Create
    c = sample_category
    r1 = auth_client.post('/incidents/create', data={
        'title':'Inc1','description':'Desc','status':'Open','category':c.id
    }, follow_redirects=False)
    assert r1.status_code == 302

    inc = Incident.query.filter_by(title='Inc1').first()
    assert inc is not None

    # List
    r2 = auth_client.get('/incidents/')
    assert b'Inc1' in r2.data

    # View
    r3 = auth_client.get(f'/incidents/{inc.id}')
    assert b'Desc' in r3.data

    # Edit
    r4 = auth_client.post(f'/incidents/{inc.id}/edit', data={
        'title':'Inc1u','description':'Desc2','status':'Closed','category':c.id
    }, follow_redirects=False)
    assert r4.status_code == 302
    assert Incident.query.get(inc.id).status == 'Closed'

    # Delete
    r5 = auth_client.post(f'/incidents/{inc.id}/delete', follow_redirects=False)
    assert r5.status_code == 302
    assert Incident.query.get(inc.id) is None
