from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .api.v1_api_keys import router as api_keys_router
from .api.v1_auth import router as auth_router
from .api.v1_cars import router as cars_router
from .api.v1_users import router as users_router
from .api.v1_payments import router as payments_router
from .api.v1_orders import router as orders_router
from .database import Base, engine, get_db
from .models import User


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Car Showroom API",
    description="A developer-focused car marketplace API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rate limiter
app.add_middleware(
    RateLimitMiddleware,
    max_requests=60,
    window_seconds=60,
)


app.include_router(auth_router)
app.include_router(cars_router)
app.include_router(users_router)
app.include_router(api_keys_router)
app.include_router(payments_router)
app.include_router(orders_router)



@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "car-showroom-api",
    }


@app.get("/api/health/db")
def database_health(
    db: Session = Depends(get_db),
):
    result = db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
        "result": result.scalar(),
    }
