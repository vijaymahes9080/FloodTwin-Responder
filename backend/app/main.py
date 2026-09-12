"""
Main Application Entrypoint for FLOODTWIN RESPONDER.
Human-supervised disaster decision support backend service.
"""

import sys
import time
import uuid
from contextlib import asynccontextmanager

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.assets import router as assets_router
from backend.app.api.audit import router as audit_router
from backend.app.api.health import router as health_router
from backend.app.api.policy import router as policy_router
from backend.app.api.reports import router as reports_router
from backend.app.api.response_briefs import router as briefs_router
from backend.app.api.risk import router as risk_router
from backend.app.api.sensors import router as sensors_router
from backend.app.core.config import settings
from backend.app.core.security import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logging
    print("==================================================================")
    print(f"[STARTUP] FLOODTWIN RESPONDER API Service v{settings.VERSION} Starting...")
    print(f"[DISTRICT] Operational District: {settings.DISTRICT_NAME}")
    print(f"[SAFETY] Safety Invariant: Autonomous Alerts BANNED (HITL Mandatory)")
    print(f"[NOTIFICATION] Notification Provider: MockAlertProvider (SANDBOX MODE)")
    print("==================================================================")
    yield
    print("[SHUTDOWN] Shutting down FLOODTWIN RESPONDER API Service.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "Human-Supervised Flood Intelligence and Response-Planning Platform. "
        "Strictly provides decision support without autonomous alert dispatch."
    ),
    lifespan=lifespan
)

# 1. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Defensive Security Headers
app.add_middleware(SecurityHeadersMiddleware)


# 3. Request ID & Structured Telemetry Middleware
@app.middleware("http")
async def request_tracing_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or f"REQ-{uuid.uuid4().hex[:8]}"
    start_time = time.time()
    
    # Attach request_id to state
    request.state.request_id = request_id
    
    response = await call_next(request)
    
    process_time = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(process_time)
    
    return response


# 4. Global Exception Handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    req_id = getattr(request.state, "request_id", "UNKNOWN")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. State safely preserved.",
            "details": str(exc),
            "request_id": req_id
        }
    )


# 5. Include API Routers
app.include_router(health_router)
app.include_router(reports_router, prefix=settings.API_PREFIX)
app.include_router(sensors_router, prefix=settings.API_PREFIX)
app.include_router(assets_router, prefix=settings.API_PREFIX)
app.include_router(risk_router, prefix=settings.API_PREFIX)
app.include_router(briefs_router, prefix=settings.API_PREFIX)
app.include_router(audit_router, prefix=settings.API_PREFIX)
app.include_router(policy_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "OPERATIONAL",
        "docs_url": "/docs",
        "health_url": "/health",
        "mock_notification_mode": True
    }
