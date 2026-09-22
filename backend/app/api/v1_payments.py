import stripe

from fastapi import APIRouter, HTTPException, Request
from sqlalchemy.orm import Session

from ..config import settings
from ..database import SessionLocal
from ..models import Order


router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Payments"],
)


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()

    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            settings.stripe_webhook_secret,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature",
        )

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"].to_dict()

        metadata = session.get("metadata") or {}
        order_id = metadata.get("order_id")

        if not order_id:
            return {
                "received": True,
                "message": "No order_id in metadata",
            }

        db: Session = SessionLocal()

        try:
            order = (
                db.query(Order)
                .filter(Order.id == int(order_id))
                .first()
            )

            if order is None:
                raise HTTPException(
                    status_code=404,
                    detail="Order not found",
                )

            order.status = "paid"
            order.stripe_session_id = session["id"]

            db.commit()

        finally:
            db.close()

    return {
        "received": True,
    }