import hashlib
import sys
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import settings
from app.limiter import _get_remote_ip, limiter

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer()
        if settings.env == "development"
        else structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(0),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

log = structlog.get_logger()


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    if settings.env == "production" and settings.admin_api_key == "changeme":
        log.error(
            "ADMIN_API_KEY is set to the default value 'changeme'. "
            "Refusing to start in production. Set a secure ADMIN_API_KEY "
            "in your environment or .env file."
        )
        sys.exit(1)
    log.info("api_starting", env=settings.env)
    yield
    log.info("api_shutting_down")


app = FastAPI(
    title="pre.voto API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:4321",
        "https://pre.voto",
        "https://www.pre.voto",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        headers=exc.headers,
        content={
            "error": {
                "code": f"http_{exc.status_code}",
                "message": str(exc.detail),
                "detail": None,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Sanitize errors: Pydantic v2 ctx may contain non-serializable objects
    safe_errors = []
    for err in exc.errors():
        clean = {k: v for k, v in err.items() if k != "ctx"}
        safe_errors.append(clean)
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "validation_error",
                "message": "Request validation failed",
                "detail": safe_errors,
            }
        },
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "error": {
                "code": "rate_limit_exceeded",
                "message": "Too many requests",
                "detail": str(exc.detail),
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    log.exception("unhandled_exception", path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": "Internal server error",
                "detail": None,
            }
        },
    )


# ---------------------------------------------------------------------------
# Request logging middleware
# ---------------------------------------------------------------------------

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = round((time.perf_counter() - start) * 1000, 1)

    ip = _get_remote_ip(request)
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()[:16]

    # Extract country code from path (e.g. /candidates/co -> co)
    path_parts = request.url.path.strip("/").split("/")
    country_requested = None
    if len(path_parts) >= 2:
        potential_country = path_parts[1]
        if len(potential_country) == 2 and potential_country.isalpha():
            country_requested = potential_country.lower()

    log.info(
        "request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        latency_ms=latency_ms,
        ip_hash=ip_hash,
        country_requested=country_requested,
    )

    return response


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from app.routers.admin import router as admin_router  # noqa: E402
from app.routers.articles import router as articles_router  # noqa: E402
from app.routers.candidates import router as candidates_router  # noqa: E402
from app.routers.countries import router as countries_router  # noqa: E402
from app.routers.donations import router as donations_router  # noqa: E402
from app.routers.feature_flags import router as feature_flags_router  # noqa: E402
from app.routers.og import og_router, share_router  # noqa: E402
from app.routers.polls import router as polls_router  # noqa: E402
from app.routers.quiz import router as quiz_router  # noqa: E402
from app.routers.stripe_webhook import router as stripe_webhook_router  # noqa: E402
from app.routers.subscribers import router as subscribers_router  # noqa: E402
from app.routers.usage import admin_usage_router, router as usage_router  # noqa: E402

app.include_router(countries_router)
app.include_router(candidates_router)
app.include_router(quiz_router)
app.include_router(articles_router)
app.include_router(polls_router)
app.include_router(subscribers_router)
app.include_router(donations_router)
app.include_router(feature_flags_router)
app.include_router(admin_router)
app.include_router(og_router)
app.include_router(share_router)
app.include_router(stripe_webhook_router)
app.include_router(usage_router)
app.include_router(admin_usage_router)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}
