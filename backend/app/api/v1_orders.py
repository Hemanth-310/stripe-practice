from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .dependencies.auth import get_current_user
from ..database import get_db
from ..models import Car, Order, User
from ..services.stripe import create_checkout_session


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)


@router.post(
    "/{car_id}/checkout",
)
def create_order_checkout(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    car = (
        db.query(Car)
        .filter(
            Car.id == car_id,
            Car.is_available == True,
        )
        .first()
    )

    if car is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Available car not found",
        )

    order = Order(
        user_id=current_user.id,
        car_id=car.id,
        amount=float(car.price),
        status="pending",
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    session = create_checkout_session(
        order_id=order.id,
        car_name=f"{car.brand} {car.model}",
        amount=float(car.price),
    )

    order.stripe_session_id = session.id

    db.commit()

    return {
        "order_id": order.id,
        "status": order.status,
        "checkout_url": session.url,
    }
