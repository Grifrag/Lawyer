import pytest
from app.models import User

def test_register(client):
    resp = client.post("/api/auth/register", json={
        "email": "new@example.com", "password": "secure123", "name": "Test"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["message"] == "registered"

def test_register_duplicate(client, user):
    resp = client.post("/api/auth/register", json={
        "email": "test@example.com", "password": "x"
    })
    assert resp.status_code == 409

def test_login_success(client, user):
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com", "password": "password123"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()

def test_login_wrong_password(client, user):
    resp = client.post("/api/auth/login", json={
        "email": "test@example.com", "password": "wrong"
    })
    assert resp.status_code == 401

def test_protected_requires_jwt(client):
    resp = client.get("/api/cases")
    assert resp.status_code == 401

def test_email_not_verified_blocked(client, db):
    import bcrypt
    pw = bcrypt.hashpw(b"pw", bcrypt.gensalt()).decode()
    u = User(email="unverified@x.com", password_hash=pw,
             email_verified=False, subscription_status="active")
    db.session.add(u)
    db.session.commit()
    resp = client.post("/api/auth/login",
                       json={"email": "unverified@x.com", "password": "pw"})
    token = resp.get_json()["access_token"]
    resp2 = client.get("/api/cases",
                       headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 403
    assert resp2.get_json()["error"] == "email_not_verified"

def test_verify_email(client, db):
    import bcrypt
    pw = bcrypt.hashpw(b"pw", bcrypt.gensalt()).decode()
    u = User(email="v@x.com", password_hash=pw,
             email_verified=False, email_verify_token="abc123")
    db.session.add(u)
    db.session.commit()
    resp = client.post("/api/auth/verify-email", json={"token": "abc123"})
    assert resp.status_code == 200
    db.session.refresh(u)
    assert u.email_verified is True
    assert u.email_verify_token is None

def test_forgot_password_always_200(client, user):
    # Returns 200 even for unknown email (no user enumeration)
    resp = client.post("/api/auth/forgot-password", json={"email": "nosuchuser@x.com"})
    assert resp.status_code == 200

def test_reset_password_success(client, db):
    import bcrypt
    from datetime import datetime, timedelta
    pw = bcrypt.hashpw(b"old", bcrypt.gensalt()).decode()
    u = User(email="r@x.com", password_hash=pw, email_verified=True,
             reset_password_token="tok123",
             reset_token_expires=datetime.utcnow() + timedelta(hours=1))
    db.session.add(u)
    db.session.commit()
    resp = client.post("/api/auth/reset-password",
                       json={"token": "tok123", "password": "newpass"})
    assert resp.status_code == 200
    db.session.refresh(u)
    assert u.reset_password_token is None
    assert bcrypt.checkpw(b"newpass", u.password_hash.encode())

def test_reset_password_expired(client, db):
    import bcrypt
    from datetime import datetime, timedelta
    pw = bcrypt.hashpw(b"old", bcrypt.gensalt()).decode()
    u = User(email="exp@x.com", password_hash=pw, email_verified=True,
             reset_password_token="expiredtok",
             reset_token_expires=datetime.utcnow() - timedelta(hours=2))
    db.session.add(u)
    db.session.commit()
    resp = client.post("/api/auth/reset-password",
                       json={"token": "expiredtok", "password": "newpass"})
    assert resp.status_code == 400
