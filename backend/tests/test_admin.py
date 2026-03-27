def test_admin_guard_rejects_non_admin(client, auth_headers):
    resp = client.get("/api/admin/users", headers=auth_headers)
    assert resp.status_code == 403


def test_admin_users_list(client, db, auth_headers):
    from app.models import User
    user = User.query.filter_by(email="test@example.com").first()
    user.is_admin = True
    db.session.commit()
    resp = client.get("/api/admin/users", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(u["email"] == "test@example.com" for u in data)


def test_admin_stats(client, db, auth_headers):
    from app.models import User
    user = User.query.filter_by(email="test@example.com").first()
    user.is_admin = True
    db.session.commit()
    resp = client.get("/api/admin/stats", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "total_users" in data
    assert "active_subscriptions" in data
    assert "checks_today" in data
    assert "errors_today" in data
