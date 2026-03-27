import os
import stripe
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.billing import bp
from app.extensions import db
from app.models import User

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
PRICE_ID = os.environ.get("STRIPE_PRICE_ID", "")
WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
DOMAIN = os.environ.get("APP_DOMAIN", "http://localhost:5173")

@bp.route("/status", methods=["GET"])
@jwt_required()
def billing_status():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    return jsonify({
        "subscription_status": user.subscription_status,
        "stripe_subscription_id": user.stripe_subscription_id,
    }), 200

@bp.route("/checkout", methods=["POST"])
@jwt_required()
def checkout():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    if not user.stripe_customer_id:
        customer = stripe.Customer.create(email=user.email,
                                          name=user.name or user.email)
        user.stripe_customer_id = customer.id
        db.session.commit()
    session = stripe.checkout.Session.create(
        customer=user.stripe_customer_id,
        payment_method_types=["card"],
        line_items=[{"price": PRICE_ID, "quantity": 1}],
        mode="subscription",
        success_url=f"{DOMAIN}/billing?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{DOMAIN}/billing",
    )
    return jsonify({"url": session.url}), 200

@bp.route("/portal", methods=["POST"])
@jwt_required()
def portal():
    uid = int(get_jwt_identity())
    user = db.session.get(User, uid)
    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url=f"{DOMAIN}/billing",
    )
    return jsonify({"url": session.url}), 200

@bp.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    obj = event["data"]["object"]

    STATUS_MAP = {
        "customer.subscription.created": "active",
        "customer.subscription.deleted": "cancelled",
    }

    if event["type"] in STATUS_MAP:
        user = User.query.filter_by(stripe_customer_id=obj["customer"]).first()
        if user:
            user.stripe_subscription_id = obj["id"]
            user.subscription_status = STATUS_MAP[event["type"]]
            db.session.commit()

    elif event["type"] == "customer.subscription.updated":
        user = User.query.filter_by(stripe_customer_id=obj["customer"]).first()
        if user:
            user.subscription_status = obj["status"]
            db.session.commit()

    elif event["type"] == "invoice.payment_failed":
        user = User.query.filter_by(stripe_customer_id=obj["customer"]).first()
        if user:
            user.subscription_status = "past_due"
            db.session.commit()
            from app.auth.utils import send_email
            send_email(
                user.email,
                "Solon Checker — Αποτυχία πληρωμής συνδρομής",
                "<p>Η πληρωμή της συνδρομής σας απέτυχε. "
                "Παρακαλώ ενημερώστε τα στοιχεία πληρωμής σας μέσω του "
                "<a href='/billing'>Διαχείριση Συνδρομής</a>.</p>"
            )

    elif event["type"] == "invoice.payment_succeeded":
        user = User.query.filter_by(stripe_customer_id=obj["customer"]).first()
        if user:
            user.subscription_status = "active"
            db.session.commit()

    return jsonify({"received": True}), 200
