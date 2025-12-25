import sys
import os

# Load environment variables BEFORE importing modules that need them
from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from arq import create_pool
from arq.connections import RedisSettings
from routers import projects, docs, system, auth, context

# Import security modules
from services.error_handler import error_handler, create_error_response
from services.security_monitoring import security_monitor
from services.security_config import SecurityConfig, SecurityConstants

# Import security middleware
security_middleware_available = False
try:
    from services.security_middleware import (
        SecureErrorMiddleware, 
        SecurityHeadersMiddleware,
        SecurityEventLogger
    )
    security_middleware_available = True
except ImportError:
    print("Warning: Security middleware not available")

# Import input validation middleware
input_validation_available = False
try:
    from middleware.input_validation import InputValidationMiddleware, rate_limiter
    input_validation_available = True
except ImportError:
    print("Warning: Input validation middleware not available")
    InputValidationMiddleware = None
    rate_limiter = None

app = FastAPI(title="ArchIntel Docs Backend")

# CORS setup
allowed_origins = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Add security middleware
if security_middleware_available:
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(SecureErrorMiddleware, enable_detailed_errors=False)
else:
    print("Warning: Security middleware not available, skipping middleware registration")

# Add input validation middleware
if input_validation_available and InputValidationMiddleware:
    app.add_middleware(InputValidationMiddleware, rate_limiter=rate_limiter)
    print("Input validation middleware added")
else:
    print("Warning: Input validation middleware not available, skipping middleware registration")

@app.on_event("startup")
async def startup_event():
    # Use redis://localhost:6379 by default or whatever is in env
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    source = "env" if os.getenv("REDIS_URL") else "default"
    try:
        app.state.arq_pool = await create_pool(RedisSettings.from_dsn(redis_url))
        print(f"Connected to Redis for background tasks at {redis_url} (source: {source})")
    except Exception as e:
        print(f"Warning: Could not connect to Redis at {redis_url} (source: {source}). Background tasks will be disabled. Error: {e}")
        app.state.arq_pool = None
    
    # Initialize security logging
    if security_middleware_available:
        SecurityEventLogger.log_auth_attempt("SYSTEM", "SYSTEM", True, "startup", "Backend started successfully")
    else:
        print("Warning: Security logging not available")

@app.on_event("shutdown")
async def shutdown_event():
    if hasattr(app.state, "arq_pool") and app.state.arq_pool:
        await app.state.arq_pool.close()
    
    # Log shutdown event
    if security_middleware_available:
        SecurityEventLogger.log_auth_attempt("SYSTEM", "SYSTEM", True, "shutdown", "Backend shutdown")
    else:
        print("Warning: Security logging not available during shutdown")

# Include routers for modular endpoints
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(docs.router, prefix="/docs", tags=["Docs"])
app.include_router(context.router, prefix="/context", tags=["Context"])
app.include_router(system.router, prefix="/system", tags=["System"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

# Import CSP router if available
try:
    from routers.csp import csp_router
    app.include_router(csp_router)
    print("CSP violation reporting endpoint added: POST /api/v1/csp-report")
    print("CSP status endpoint added: GET /api/v1/csp-status")
except ImportError as e:
    print(f"Warning: CSP router not available ({e}), skipping CSP endpoints")
except Exception as e:
    print(f"Warning: Error loading CSP router ({e}), skipping CSP endpoints")

@app.get("/")
def root():
    return {"message": "ArchIntel Docs Backend is running."}

# Global error handlers

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions"""
    try:
        # Get client IP for logging
        client_ip = request.client.host if request.client else "unknown"
        
        # Handle the error using our error handler
        error_response = error_handler.handle_error(exc, request)
        
        # Log security event for critical errors
        if hasattr(exc, 'severity') and exc.severity == "CRITICAL":
            SecurityEventLogger.log_auth_attempt(
                client_ip, None, False, request.url.path, 
                f"Critical error: {str(exc)[:100]}"
            )
        
        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={"X-Content-Type-Options": "nosniff"}
        )
    except Exception as handler_error:
        # Fallback error response if our handler fails
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An internal server error occurred",
                    "timestamp": "2025-01-01T00:00:00Z",
                    "path": str(request.url.path)
                }
            }
        )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    """HTTP exception handler with security logging"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Log failed authentication attempts
    if exc.status_code == 401:
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, request.url.path, 
            f"Authentication failed: {exc.detail}"
        )
    elif exc.status_code == 403:
        SecurityEventLogger.log_auth_attempt(
            client_ip, None, False, request.url.path, 
            f"Authorization failed: {exc.detail}"
        )
    
    # Use our error handler for consistent formatting
    error_response = error_handler.handle_http_exception(exc, request)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
        headers={"X-Content-Type-Options": "nosniff"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Request validation error handler"""
    client_ip = request.client.host if request.client else "unknown"
    
    # Log validation errors
    SecurityEventLogger.log_auth_attempt(
        client_ip, None, False, request.url.path, 
        f"Validation error: {str(exc)[:200]}"
    )
    
    error_response = create_error_response(
        "INVALID_INPUT",
        "Request validation failed",
        400,
        request
    )
    
    return error_response

# Health check endpoint with security status
@app.get("/health")
async def health_check():
    """Health check endpoint with security status"""
    try:
        # Check Redis connection
        redis_status = "connected" if hasattr(app.state, "arq_pool") and app.state.arq_pool else "disconnected"
        
        # Get security status
        security_status = {
            "timestamp": "2025-01-01T00:00:00Z",
            "redis_status": redis_status,
            "security_enabled": security_middleware_available,
            "input_validation_enabled": input_validation_available,
            "monitoring_active": True
        }
        
        # Add security monitoring status if available
        try:
            monitoring_status = security_monitor.get_security_status()
            security_status.update({
                "error_count": monitoring_status["metrics"]["total_errors"],
                "security_errors": monitoring_status["metrics"]["security_errors"],
                "alerts_generated": monitoring_status["metrics"]["alerts_generated"],
                "risk_level": monitoring_status.get("active_monitoring", {}).get("risk_level", "UNKNOWN")
            })
        except Exception:
            security_status["monitoring_errors"] = "Unable to get monitoring status"
        
        return {
            "status": "healthy",
            "service": "ArchIntel Backend",
            "version": "1.0.0",
            "security": security_status
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "ArchIntel Backend",
            "error": str(e),
            "security": {
                "security_enabled": security_middleware_available,
                "input_validation_enabled": input_validation_available
            }
        }

# Security status endpoint
@app.get("/security/status")
async def security_status():
    """Security status and monitoring information"""
    try:
        # Get security monitoring status
        status = security_monitor.get_security_status()
        
        # Add system configuration
        config = SecurityConfig.get_security_policy()
        
        return {
            "timestamp": "2025-01-01T00:00:00Z",
            "security_status": status,
            "configuration": config,
            "features": {
                "error_handling": True,
                "security_monitoring": True,
                "rate_limiting": input_validation_available,
                "security_headers": security_middleware_available
            }
        }
    except Exception as e:
        return {
            "error": "Unable to retrieve security status",
            "details": str(e)
        }
