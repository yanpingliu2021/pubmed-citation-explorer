"""pytest tests for library"""
import sys
import pytest
sys.path.append("../flask_app")

#flask app
from web import application

@pytest.fixture
def client():
    """Generic Flask application fixture"""

    application.testing = True
    return application.test_client()

def test_root(client):
    """Tests that a redirect is in place for root"""

    # A GET request should return a 200
    res_get = client.get('/')

    assert res_get.status_code == 200

def test_background(client):
    """Test the Basics are working"""

    # A GET request should return a 200
    res_get = client.get('/background_process')
    assert res_get.status_code == 200

    # Pass query string to GET request
    res_get = client.get('/background_process', query_string={'Category':'title', "Year":1979})
    assert res_get.status_code == 200
    assert res_get.json['image_file'] == 'static/images/title_1979.png'

    # A POST request should return a 200
    res_post = client.post('/background_process', json={'Category':'title', "Year":1979})
    assert res_post.status_code == 200
    assert res_post.content_type == 'application/json'
    assert res_post.json['image_file'] == 'static/images/title_1979.png'

    # pass wrong value to POST should return status code of 500
    with pytest.raises(KeyError):
        res_post = client.post('/background_process', json={'Category':'title', "XXXX":1979})
