import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import EnmaskException
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    CorrelationIdMiddleware,
)
from app.core.rate_limiter import limiter, rate_limit_handler
from slowapi.errors import RateLimitExceeded

from app.api.routers import connections, rules, jobs, reports
from app.api.routers.auth import router as auth_router
from app.api.v2.router import router as v2_router

import app.core.logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Enmask backend starting up")
    try:
        from app.infrastructure.plugins.loader import plugin_loader
        plugin_loader.load_all()
    except Exception as exc:
        logger.warning("Plugin loader error: %s", exc)
    yield
    logger.info("Enmask backend shutting down")
    try:
        from app.infrastructure.plugins.loader import plugin_loader
        for name in list(plugin_loader._plugins.keys()):
            plugin_loader.unload_plugin(name)
    except Exception:
        pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

allow_origins = settings.cors_origins_list()
if allow_origins:
    allow_credentials = True
    if len(allow_origins) == 1 and allow_origins[0] == "*":
        allow_credentials = False

    cors_kwargs = dict(
        allow_origins=allow_origins,
        allow_credentials=allow_credentials,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-API-KEY", "X-Request-ID"],
    )
    origin_regex = settings.cors_origin_regex()
    if origin_regex:
        cors_kwargs["allow_origin_regex"] = origin_regex

    app.add_middleware(CORSMiddleware, **cors_kwargs)


@app.exception_handler(EnmaskException)
async def enmask_exception_handler(request: Request, exc: EnmaskException) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception on %s %s: %s", request.method, request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


try:
    from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
    from starlette.responses import Response

    REQUEST_COUNT = Counter(
        "enmask_http_requests_total",
        "Total HTTP requests",
        ["method", "endpoint", "status_code"],
    )
    REQUEST_LATENCY = Histogram(
        "enmask_http_request_duration_seconds",
        "HTTP request latency in seconds",
        ["method", "endpoint"],
    )

    @app.middleware("http")
    async def prometheus_middleware(request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start
        path = request.url.path
        if path != "/metrics":
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=path,
                status_code=response.status_code,
            ).inc()
            REQUEST_LATENCY.labels(
                method=request.method,
                endpoint=path,
            ).observe(duration)
        return response

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

except ImportError:
    pass

try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    provider = TracerProvider()
    trace.set_tracer_provider(provider)
except ImportError:
    pass


app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(connections.router, prefix=settings.API_V1_STR)
app.include_router(rules.router, prefix=settings.API_V1_STR)
app.include_router(jobs.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(v2_router, prefix="/api/v2")


@app.get("/health")
async def health_check():
    dependencies = {}
    try:
        from app.api.deps import get_connection_repository
        repo = await get_connection_repository()
        dependencies["repository"] = "ok"
    except Exception:
        dependencies["repository"] = "unavailable"

    try:
        from app.core.config import settings as s
        if s.REDIS_URL:
            import redis
            r = redis.from_url(s.REDIS_URL, socket_connect_timeout=2)
            r.ping()
            dependencies["redis"] = "ok"
        else:
            dependencies["redis"] = "not_configured"
    except Exception:
        dependencies["redis"] = "unavailable"

    all_ok = all(v in ("ok", "not_configured") for v in dependencies.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "service": "enmask-backend",
        "api_prefix": settings.API_V1_STR,
        "dependencies": dependencies,
    }


@app.get(f"{settings.API_V1_STR}/meta", tags=["meta"])
def api_meta():
    return {
        "service": "enmask-backend",
        "auth": "google",
        "api_prefix": settings.API_V1_STR,
        "has_register": False,
    }
