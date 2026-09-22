from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .dependencies.roles import require_admin
from .dependencies.auth import get_current_user
from ..database import get_db
from ..models import Car, User
from ..schemas.car import CarCreate, CarResponse, CarUpdate


router = APIRouter(
    prefix="/api/v1/cars",
    tags=["Cars"],
)


@router.get(
    "",
    response_model=list[CarResponse],
)
def list_cars(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Car)
        .order_by(Car.id.desc())
        .all()
    )


@router.post(
    "",
    response_model=CarResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_car(
    request: CarCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    car = Car(
        brand=request.brand,
        model=request.model,
        year=request.year,
        price=request.price,
        description=request.description,
        is_available=True,
    )

    db.add(car)
    db.commit()
    db.refresh(car)

    return car


@router.get(
    "/{car_id}",
    response_model=CarResponse,
)
def get_car(
    car_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    car = db.query(Car).filter(Car.id == car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )

    return car


@router.patch(
    "/{car_id}",
    response_model=CarResponse,
)
def update_car(
    car_id: int,
    request: CarUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    car = db.query(Car).filter(Car.id == car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )

    update_data = request.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(car, field, value)

    db.commit()
    db.refresh(car)

    return car


@router.delete(
    "/{car_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_car(
    car_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    car = db.query(Car).filter(Car.id == car_id).first()

    if car is None:
        raise HTTPException(
            status_code=404,
            detail="Car not found",
        )

    db.delete(car)
    db.commit()

    return None