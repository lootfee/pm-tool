import pytest
from tests import app, testing_client, db
from pymongo import MongoClient

@pytest.fixture
def client():
    app = app('TestConfig')
    client = app.test_client()
    
    # You can add setup/teardown logic here, e.g., clearing collections after tests.
    
    yield client

    # Cleanup logic if needed
    test_client.drop_database('test_db')