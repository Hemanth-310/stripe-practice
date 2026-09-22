import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):

    def __init__(
        self,
        app,
        max_requests: int = 60,
        window_seconds: int = 60,
    ):
        super().__init__(app)

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def dispatch(self, request: Request, call_next):

        client_ip = request.client.host
        now = time.time()

        history = self.requests.get(client_ip, [])

        history = [
            timestamp
            for timestamp in history
            if now - timestamp < self.window_seconds
        ]

        if len(history) >= self.max_requests:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded"
                },
            )

        history.append(now)
        self.requests[client_ip] = history

        return await call_next(request)
