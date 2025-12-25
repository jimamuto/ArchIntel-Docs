"""
CSP Violation Reporting Service for ArchIntel Backend

This module provides comprehensive CSP violation reporting and handling:
- CSP violation endpoint for browser reports
- Violation analysis and categorization
- Security monitoring integration
- Alert generation for potential security issues

Author: ArchIntel Security Team
Requirements: CSP violation reporting and security monitoring
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import Request, HTTPException
from pydantic import BaseModel, validator
from collections import defaultdict

# Import security modules
from services.security_monitoring import security_monitor
from services.security_config import SecurityConfig, SecurityConstants
from services.security_utils import SecurityUtils


class CSPViolationReport(BaseModel):
    """CSP violation report model"""
    document_uri: str
    referrer: str = ""
    violated_directive: str
    effective_directive: str
    original_policy: str
    blocked_uri: str = ""
    source_file: str = ""
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    status_code: Optional[int] = None
    script_sample: str = ""
    
    @validator('document_uri', 'violated_directive', 'effective_directive', 'original_policy')
    def validate_required_fields(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError('Required field cannot be empty')
        return v
    
    class Config:
        extra = "allow"  # Allow additional fields from browser reports


class CSPViolationAnalyzer:
    """Analyze and categorize CSP violations"""
    
    def __init__(self):
        self.logger = logging.getLogger("archintel.csp")
        self.violation_counts = defaultdict(int)
        self.suspicious_patterns = [
            'eval(', 'Function(', 'setTimeout(', 'setInterval(',
            'document.write(', 'document.writeln(',
            'javascript:', 'data:text/html',
            'blob:', 'data:application/javascript'
        ]
    
    def analyze_violation(self, report: CSPViolationReport, client_ip: str) -> Dict[str, Any]:
        """Analyze CSP violation and determine severity"""
        
        # Categorize violation type
        violation_type = self._categorize_violation(report)
        
        # Check for suspicious patterns
        is_suspicious = self._check_suspicious_patterns(report)
        
        # Check for potential XSS
        is_potential_xss = self._check_potential_xss(report)
        
        # Generate risk assessment
        risk_level = self._assess_risk(violation_type, is_suspicious, is_potential_xss)
        
        # Update violation statistics
        self.violation_counts[f"{report.effective_directive}:{violation_type}"] += 1
        
        # Log the violation
        self._log_violation(report, client_ip, violation_type, risk_level)
        
        # Generate security alert if high risk
        if risk_level in ['HIGH', 'CRITICAL']:
            self._generate_security_alert(report, client_ip, violation_type, risk_level)
        
        return {
            "violation_type": violation_type,
            "is_suspicious": is_suspicious,
            "is_potential_xss": is_potential_xss,
            "risk_level": risk_level,
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip
        }
    
    def _categorize_violation(self, report: CSPViolationReport) -> str:
        """Categorize the type of CSP violation"""
        
        # Check for inline violations
        if report.effective_directive in ['script-src', 'style-src']:
            if report.blocked_uri in ['inline', "'inline'"]:
                return "INLINE_SCRIPT_OR_STYLE"
            elif report.blocked_uri.startswith(('data:', 'blob:')):
                return "DATA_OR_BLOB_SOURCE"
        
        # Check for eval violations
        if report.effective_directive == 'script-src' and 'eval' in report.violated_directive:
            return "EVAL_VIOLATION"
        
        # Check for unauthorized domains
        if report.blocked_uri and not report.blocked_uri.startswith(('self', "'self'")):
            if report.blocked_uri.startswith(('http:', 'https:')):
                return "UNAUTHORIZED_DOMAIN"
        
        # Check for websocket violations
        if report.effective_directive == 'connect-src' and report.blocked_uri.startswith(('ws:', 'wss:')):
            return "UNAUTHORIZED_WEBSOCKET"
        
        return "OTHER_VIOLATION"
    
    def _check_suspicious_patterns(self, report: CSPViolationReport) -> bool:
        """Check for suspicious patterns in the violation"""
        
        # Check blocked URI
        if report.blocked_uri:
            for pattern in self.suspicious_patterns:
                if pattern in report.blocked_uri.lower():
                    return True
        
        # Check source file
        if report.source_file:
            for pattern in self.suspicious_patterns:
                if pattern in report.source_file.lower():
                    return True
        
        # Check script sample
        if report.script_sample:
            for pattern in self.suspicious_patterns:
                if pattern in report.script_sample.lower():
                    return True
        
        return False
    
    def _check_potential_xss(self, report: CSPViolationReport) -> bool:
        """Check if violation indicates potential XSS attack"""
        
        xss_indicators = [
            '<script', 'javascript:', 'document.cookie',
            'document.domain', 'document.write', 'eval(',
            'innerHTML', 'outerHTML', 'document.location'
        ]
        
        # Check all relevant fields for XSS indicators
        fields_to_check = [
            report.blocked_uri,
            report.source_file, 
            report.script_sample,
            report.document_uri
        ]
        
        for field in fields_to_check:
            if field:
                for indicator in xss_indicators:
                    if indicator in field.lower():
                        return True
        
        return False
    
    def _assess_risk(self, violation_type: str, is_suspicious: bool, is_potential_xss: bool) -> str:
        """Assess risk level of the violation"""
        
        # High risk violations
        high_risk_types = [
            "INLINE_SCRIPT_OR_STYLE",
            "EVAL_VIOLATION",
            "UNAUTHORIZED_DOMAIN"
        ]
        
        if is_potential_xss:
            return "CRITICAL"
        
        if is_suspicious or violation_type in high_risk_types:
            return "HIGH"
        
        if violation_type == "DATA_OR_BLOB_SOURCE":
            return "MEDIUM"
        
        return "LOW"
    
    def _log_violation(self, report: CSPViolationReport, client_ip: str, 
                      violation_type: str, risk_level: str):
        """Log CSP violation for security monitoring"""
        
        self.logger.warning(
            f"CSP_VIOLATION - IP: {client_ip}, Type: {violation_type}, "
            f"Risk: {risk_level}, Directive: {report.effective_directive}, "
            f"Blocked: {report.blocked_uri[:100]}, Document: {report.document_uri[:100]}"
        )
        
        # Add to security monitoring
        security_monitor.record_event(
            "CSP_VIOLATION",
            {
                "violation_type": violation_type,
                "risk_level": risk_level,
                "directive": report.effective_directive,
                "blocked_uri": report.blocked_uri[:200],
                "document_uri": report.document_uri[:200],
                "client_ip": client_ip
            }
        )
    
    def _generate_security_alert(self, report: CSPViolationReport, client_ip: str,
                                violation_type: str, risk_level: str):
        """Generate security alert for high-risk violations"""
        
        alert_data = {
            "type": "CSP_VIOLATION",
            "severity": risk_level,
            "timestamp": datetime.utcnow().isoformat(),
            "source_ip": client_ip,
            "violation_details": {
                "type": violation_type,
                "directive": report.effective_directive,
                "blocked_uri": report.blocked_uri,
                "document_uri": report.document_uri,
                "referrer": report.referrer
            }
        }
        
        # Generate alert
        security_monitor.generate_alert(
            alert_type="CSP_VIOLATION",
            severity=risk_level,
            message=f"High-risk CSP violation detected from {client_ip}",
            details=alert_data
        )
    
    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get CSP violation statistics"""
        return {
            "total_violations": sum(self.violation_counts.values()),
            "violation_breakdown": dict(self.violation_counts),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def reset_statistics(self):
        """Reset violation statistics"""
        self.violation_counts.clear()
        self.logger.info("CSP violation statistics reset")


class CSPReportingService:
    """CSP reporting service for handling browser violation reports"""
    
    def __init__(self):
        self.analyzer = CSPViolationAnalyzer()
        self.logger = logging.getLogger("archintel.csp")
    
    async def handle_violation_report(self, request: Request) -> Dict[str, Any]:
        """Handle CSP violation report from browser"""
        
        try:
            # Get client IP
            client_ip = SecurityUtils.get_client_ip(request)
            
            # Parse report - CSP reports come as application/csp-report
            content_type = request.headers.get("Content-Type", "")
            
            if "application/csp-report" in content_type:
                # Standard CSP report format
                report_data = await request.json()
                report_body = report_data.get("csp-report", {})
            elif "application/json" in content_type:
                # Direct JSON format
                report_body = await request.json()
            else:
                # Fallback - try to parse as JSON
                try:
                    report_body = await request.json()
                except:
                    raise HTTPException(
                        status_code=400,
                        detail="Invalid CSP report format"
                    )
            
            # Validate and process report
            report = CSPViolationReport(**report_body)
            
            # Analyze violation
            analysis = self.analyzer.analyze_violation(report, client_ip)
            
            # Return success response
            return {
                "status": "received",
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing CSP violation report: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Invalid CSP report format"
            )
    
    def get_csp_status(self) -> Dict[str, Any]:
        """Get CSP reporting status and statistics"""
        return {
            "csp_reporting_enabled": True,
            "violation_statistics": self.analyzer.get_violation_statistics(),
            "configuration": {
                "report_uri": "/api/v1/csp-report",
                "monitoring_enabled": True,
                "alerts_enabled": True
            }
        }


# Global CSP reporting service instance
csp_reporting_service = CSPReportingService()


# CSP violation endpoint handler (to be used in routers)
async def csp_violation_endpoint(request: Request):
    """CSP violation reporting endpoint"""
    return await csp_reporting_service.handle_violation_report(request)


# CSP status endpoint handler
def csp_status_endpoint():
    """CSP status endpoint"""
    return csp_reporting_service.get_csp_status()