from app.models.category import IncidentCategory

def test_category_crud(auth_client):
    # Create
    r1 = auth_client.post('/categories/create', data={
        'name':'Hard','description':'H issues'
    }, follow_redirects=False)
    assert r1.status_code == 302
    cat = IncidentCategory.query.filter_by(name='Hard').first()
    assert cat is not None

    # List
    r2 = auth_client.get('/categories/')
    assert b'Hard' in r2.data

    # Edit
    r3 = auth_client.post(f'/categories/{cat.id}/edit', data={
        'name':'Hard','description':'Updated'
    }, follow_redirects=False)
    assert r3.status_code == 302
    assert IncidentCategory.query.get(cat.id).description == 'Updated'

    # Delete
    r4 = auth_client.post(f'/categories/{cat.id}/delete', follow_redirects=False)
    assert r4.status_code == 302
    assert IncidentCategory.query.get(cat.id) is None
