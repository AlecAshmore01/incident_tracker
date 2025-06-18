def test_index_requires_login(client):
    rv = client.get('/', follow_redirects=True)
    # if anonymous, should see login page
    assert b'Login' in rv.data

def test_dashboard_data(logged_in_client):
    rv = logged_in_client.get('/api/dashboard-data')
    assert rv.is_json
    data = rv.get_json()
    # keys we expect
    assert set(data.keys()) == {
        'statuses','status_counts','dates',
        'daily_counts','cat_names','cat_counts','avg_hours'
    }
