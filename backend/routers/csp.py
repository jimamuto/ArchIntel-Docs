"""
CSP Violation Reporting Endpoint for ArchIntel Backend

This module provides the CSP violation reporting endpoint for handling
Content Security Policy violation reports from browsers.
"""

from fastapi import APIRouter, Request, Response

# Create router for CSP endpoints
csp_router = APIRouter(prefix="/api/v1", tags=["CSP Reporting"])

@csp_router.post("/csp-report")
async def csp_report_endpoint(request: Request):
    """Handle CSP violation reports from browsers"""
    from services.csp_reporting import csp_violation_endpoint
    return await csp_violation_endpoint(request)

@csp_router.get("/csp-status")
async def csp_status_endpoint():
    """Get CSP reporting status and statistics"""
    from services.csp_reporting import csp_reporting_service
    return csp_reporting_service.get_csp_status()