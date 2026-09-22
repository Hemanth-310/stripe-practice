from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .dependencies.auth import get_current_user
from ..database import get_db
from ..models import APIKey, User
from ..services.api_key import (
    generate_api_key,
    get_key_prefix,
    hash_api_key,
)


router = APIRouter(
    prefix="/api/v1/api-keys",
    tags=["API Keys"],
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
)
def create_api_key(
    name: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    raw_key = generate_api_key()

    api_key = APIKey(
        user_id=current_user.id,
        name=name,
        key_prefix=get_key_prefix(raw_key),
        key_hash=hash_api_key(raw_key),
        is_active=True,
    )

    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {
        "id": api_key.id,
        "name": api_key.name,
        "api_key": raw_key,
        "warning": "Save this API key now. It will not be shown again.",
    }
