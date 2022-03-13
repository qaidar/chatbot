import os
import tempfile

import pytest
from chatbot import create_app
from chatbot.db import get_db, init_db

# Load SQL command to create test database
with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')

@pytest.fixture
def app():
    """ Create application instance for testing """
    # Create and open temp file
    # Returns file descriptor and path
    db_fd, db_path = tempfile.mkstemp()

    # Create app in test mode
    # and set test file as database
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
    })

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """ Create client for tests """
    return app.test_client()

@pytest.fixture
def runner(app):
    """ Create a cli runner to call click commands """
    return app.test_cli_runner()