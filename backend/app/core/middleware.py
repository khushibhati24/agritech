import logging
import time

from fastapi import Request


logger = logging.getLogger("agritech")


async def logging_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    response = await call_next(request)

    processing_time = time.perf_counter() - start_time

    logger.info(
        "%s %s -> %s %.4fs",
        request.method,
        request.url.path,
        response.status_code,
        processing_time,
    )

    response.headers["X-Process-Time"] = f"{processing_time:.4f}"

    return response
