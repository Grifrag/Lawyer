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
