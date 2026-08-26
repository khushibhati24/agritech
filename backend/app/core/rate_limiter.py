import time
from collections import defaultdict
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.lock = Lock()

    def is_allowed(self, client_ip: str) -> bool:
        current_time = time.monotonic()
        window_start = current_time - settings.RATE_LIMIT_WINDOW_SECONDS

        with self.lock:
            timestamps = self.requests[client_ip]

            timestamps[:] = [
                timestamp
                for timestamp in timestamps
                if timestamp > window_start
            ]

            if len(timestamps) >= settings.RATE_LIMIT_REQUESTS:
                return False

            timestamps.append(current_time)
            return True


rate_limiter = InMemoryRateLimiter()


async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"

    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "error": "Too many requests",
            },
        )

    return await call_next(request)