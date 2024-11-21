from flask import url_for

def test_index_route(client):
    # Log in the test user first (you need a helper for that)
    response = client.get(url_for('index'))
    assert response.status_code == 200
    assert b'PM TOOL' in response.data  # Assuming 'PM TOOL' is in the rendered HTML title.

def test_post_new_project(client):
    # Log in the test user first (you need a helper for that)
    form_data = {
        'name': 'New Project',
        'description': 'Test Project Description',
        'start_date': '2024-10-10',
        'end_date': '2024-12-31',
        'monday': 8,
        'tuesday': 8,
        'wednesday': 8,
        'thursday': 8,
        'friday': 8,
        'saturday': 0
    }

    response = client.post(url_for('index'), data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert b'New Project' in response.data  # Ensure the new project title appears in the response