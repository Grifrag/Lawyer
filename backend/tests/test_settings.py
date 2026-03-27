def test_get_settings_empty(client, auth_headers):
    resp = client.get("/api/settings", headers=auth_headers)
    assert resp.status_code == 200

def test_save_and_get_settings(client, auth_headers):
    resp = client.post("/api/settings", headers=auth_headers, json={
        "notification_type": "gmail",
        "gmail_sender": "a@gmail.com",
        "gmail_recipient": "b@gmail.com",
        "gmail_app_password": "secret123"
    })
    assert resp.status_code == 200
    get = client.get("/api/settings", headers=auth_headers).get_json()
    assert get["notification_type"] == "gmail"
    assert get["gmail_sender"] == "a@gmail.com"
    # password is redacted
    assert "gmail_app_password" not in get or get.get("gmail_app_password") == ""
