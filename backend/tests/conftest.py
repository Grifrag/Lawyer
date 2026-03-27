import pytest
from app import create_app
from app.extensions import db as _db
from app.models import User
import bcrypt

@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()

@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()
        # clear tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(db):
    pw = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
    u = User(email="test@example.com", password_hash=pw, email_verified=True,
             subscription_status="active")
    db.session.add(u)
    db.session.commit()
    return u

@pytest.fixture
def auth_headers(client, user):
    resp = client.post("/api/auth/login",
                       json={"email": "test@example.com", "password": "password123"})
    token = resp.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
