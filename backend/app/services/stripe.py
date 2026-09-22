import stripe

from ..config import settings


stripe.api_key = settings.stripe_secret_key


def create_checkout_session(
    order_id: int,
    car_name: str,
    amount: float,
):
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": car_name,
                    },
                    "unit_amount": int(amount * 100),
                },
                "quantity": 1,
            }
        ],
        metadata={
            "order_id": str(order_id),
        },
        success_url="http://localhost:5500/success.html",
        cancel_url="http://localhost:5500/cancel.html",
    )

    return session