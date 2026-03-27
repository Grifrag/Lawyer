from unittest.mock import patch, MagicMock

def test_run_now_dispatches_task(client, auth_headers):
    mock_r = MagicMock()
    mock_r.exists.return_value = 0  # no lock held
    with patch("app.checks.routes._redis", return_value=mock_r):
        with patch("app.checks.routes.run_check_for_user") as mock_task:
            resp = client.post("/api/checks/run-now", headers=auth_headers)
    assert resp.status_code == 200
    mock_task.apply_async.assert_called_once()

def test_run_now_blocked_by_global_lock(client, auth_headers):
    mock_r = MagicMock()
    mock_r.exists.side_effect = lambda key: 1 if key == "check_all_lock" else 0
    with patch("app.checks.routes._redis", return_value=mock_r):
        resp = client.post("/api/checks/run-now", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "scheduled_check_running"

def test_check_status(client, auth_headers):
    mock_r = MagicMock()
    mock_r.exists.return_value = 0
    with patch("app.checks.routes._redis", return_value=mock_r):
        resp = client.get("/api/checks/status", headers=auth_headers)
    assert resp.status_code == 200
    assert "running" in resp.get_json()
