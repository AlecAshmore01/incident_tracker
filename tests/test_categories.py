def test_category_crud(logged_in_client):
    c = logged_in_client

    # create
    rv = c.post('/categories/create',
                data={'name':'Cat1','description':'Desc'},
                follow_redirects=True)
    assert b'Category created' in rv.data

    # edit
    rv = c.post('/categories/1/edit',
                data={'name':'CatX','description':'New'},
                follow_redirects=True)
    assert b'Category updated' in rv.data
    assert b'CatX' in rv.data

    # delete
    rv = c.post('/categories/1/delete', follow_redirects=True)
    assert b'Category deleted' in rv.data
