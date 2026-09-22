from datetime import datetime

from pydantic import BaseModel, Field


class CarCreate(BaseModel):
    brand: str = Field(
        min_length=1,
        max_length=100,
    )

    model: str = Field(
        min_length=1,
        max_length=100,
    )

    year: int = Field(
        ge=1886,
        le=2100,
    )

    price: float = Field(
        gt=0,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )


class CarUpdate(BaseModel):
    brand: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    model: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    year: int | None = Field(
        default=None,
        ge=1886,
        le=2100,
    )

    price: float | None = Field(
        default=None,
        gt=0,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    is_available: bool | None = None


class CarResponse(BaseModel):
    id: int
    brand: str
    model: str
    year: int
    price: float
    description: str | None
    is_available: bool
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
