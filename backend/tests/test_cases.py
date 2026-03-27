# tests/test_cases.py
def test_list_cases_empty(client, auth_headers):
    resp = client.get("/api/cases", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_add_case(client, auth_headers):
    resp = client.post("/api/cases", headers=auth_headers, json={
        "court": "Πρωτοδικείο Αθηνών", "search_type": "GAK",
        "number": "1234", "year": 2024, "description": "Test"
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["number"] == "1234"

def test_add_case_invalid_search_type(client, auth_headers):
    resp = client.post("/api/cases", headers=auth_headers, json={
        "court": "Πρωτοδικείο Αθηνών", "search_type": "INVALID",
        "number": "1", "year": 2024
    })
    assert resp.status_code == 400

def test_patch_case(client, auth_headers):
    add = client.post("/api/cases", headers=auth_headers, json={
        "court": "Πρωτοδικείο Αθηνών", "search_type": "GAK",
        "number": "1", "year": 2024
    })
    cid = add.get_json()["id"]
    resp = client.patch(f"/api/cases/{cid}", headers=auth_headers,
                        json={"active": False})
    assert resp.status_code == 200
    assert resp.get_json()["active"] is False

def test_delete_case(client, auth_headers):
    add = client.post("/api/cases", headers=auth_headers, json={
        "court": "X", "search_type": "GAK", "number": "1", "year": 2024
    })
    cid = add.get_json()["id"]
    resp = client.delete(f"/api/cases/{cid}", headers=auth_headers)
    assert resp.status_code == 200
    assert client.get("/api/cases", headers=auth_headers).get_json() == []

def test_cannot_access_other_user_case(client, db, auth_headers):
    import bcrypt
    from app.models import User, Case
    pw = bcrypt.hashpw(b"pw12345678", bcrypt.gensalt()).decode()
    u2 = User(email="other@x.com", password_hash=pw, email_verified=True,
              subscription_status="active")
    db.session.add(u2)
    db.session.commit()
    c = Case(user_id=u2.id, court="X", search_type="GAK", number="9999", year=2024)
    db.session.add(c)
    db.session.commit()
    resp = client.delete(f"/api/cases/{c.id}", headers=auth_headers)
    assert resp.status_code == 404

def test_subscription_required(client, db):
    """User without active subscription cannot access cases."""
    import bcrypt
    from app.models import User
    pw = bcrypt.hashpw(b"password123", bcrypt.gensalt()).decode()
    u = User(email="inactive@x.com", password_hash=pw,
             email_verified=True, subscription_status="inactive")
    db.session.add(u)
    db.session.commit()
    # Login to get token
    resp = client.post("/api/auth/login",
                       json={"email": "inactive@x.com", "password": "password123"})
    token = resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    resp2 = client.get("/api/cases", headers=headers)
    assert resp2.status_code == 403

def test_case_results_endpoint(client, auth_headers, db):
    """GET /api/cases/:id/results returns result history."""
    from app.models import Case, Result
    from app.extensions import db as _db
    # Get the user ID from the fixture
    from app.models import User
    user = User.query.filter_by(email="test@example.com").first()
    c = Case(user_id=user.id, court="X", search_type="GAK", number="1", year=2024)
    _db.session.add(c)
    _db.session.commit()
    r = Result(case_id=c.id, result_text="Pending", decision_number=None)
    _db.session.add(r)
    _db.session.commit()
    resp = client.get(f"/api/cases/{c.id}/results", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 1

def test_add_case_invalid_year(client, auth_headers):
    """Non-numeric year returns 400."""
    resp = client.post("/api/cases", headers=auth_headers, json={
        "court": "X", "search_type": "GAK", "number": "1", "year": "notayear"
    })
    assert resp.status_code == 400
