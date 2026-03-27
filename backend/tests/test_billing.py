from unittest.mock import patch, MagicMock


def test_billing_status_active(client, auth_headers):
    resp = client.get("/api/billing/status", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()["subscription_status"] == "active"  # fixture user is active


def test_checkout_creates_session(client, auth_headers):
    mock_session = MagicMock()
    mock_session.url = "https://checkout.stripe.com/fake"
    with patch("stripe.checkout.Session.create", return_value=mock_session):
        with patch("stripe.Customer.create", return_value=MagicMock(id="cus_test")):
            resp = client.post("/api/billing/checkout", headers=auth_headers)
    assert resp.status_code == 200
    assert "url" in resp.get_json()


def test_webhook_subscription_active(client, db):
    import json
    payload = json.dumps({
        "type": "customer.subscription.created",
        "data": {"object": {
            "id": "sub_test", "status": "active",
            "customer": "cus_test"
        }}
    }).encode()
    with patch("stripe.Webhook.construct_event", return_value=json.loads(payload)):
        resp = client.post("/api/billing/webhook",
                           data=payload,
                           content_type="application/json",
                           headers={"Stripe-Signature": "fake"})
    assert resp.status_code == 200


def test_portal_creates_session(client, auth_headers, db):
    from app.models import User
    user = User.query.filter_by(email="test@example.com").first()
    user.stripe_customer_id = "cus_test"
    db.session.commit()
    mock_session = MagicMock()
    mock_session.url = "https://billing.stripe.com/fake"
    with patch("stripe.billing_portal.Session.create", return_value=mock_session):
        resp = client.post("/api/billing/portal", headers=auth_headers)
    assert resp.status_code == 200
    assert "url" in resp.get_json()
