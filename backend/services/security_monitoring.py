"""
Security Monitoring Middleware for ArchIntel Backend

This module provides security monitoring and alerting capabilities including:
- Error pattern detection for potential attacks
- Security event correlation
- Alert generation for suspicious activities
- Security metrics collection
- Incident response logging

Author: ArchIntel Security Team
Requirements: Security monitoring and alerting
"""

import logging
import os
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

# Import security utilities
from services.error_handler import error_handler, ERROR_CATEGORIES, ERROR_SEVERITY, ERROR_CODES

# Configure security monitoring
security_logger = logging.getLogger("archintel.security")
monitoring_logger = logging.getLogger("archintel.monitoring")


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertType(Enum):
    """Alert types for different security events"""
    BRUTE_FORCE = "BRUTE_FORCE"
    SUSPICIOUS_REQUEST = "SUSPICIOUS_REQUEST"
    RATE_LIMIT_ABUSE = "RATE_LIMIT_ABUSE"
    ERROR_SPIKE = "ERROR_SPIKE"
    SECURITY_SCAN = "SECURITY_SCAN"
    INVALID_INPUT_PATTERN = "INVALID_INPUT_PATTERN"
    AUTHENTICATION_FAILURE_SPIKE = "AUTHENTICATION_FAILURE_SPIKE"


@dataclass
class SecurityAlert:
    """Security alert data structure"""
    alert_type: AlertType
    severity: AlertSeverity
    message: str
    ip_address: str
    timestamp: datetime
    details: Dict[str, any]
    risk_score: int = 0


@dataclass
class RequestPattern:
    """Request pattern for anomaly detection"""
    ip_address: str
    endpoint: str
    method: str
    timestamp: datetime
    status_code: int
    user_agent: str


class SecurityMonitor:
    """Security monitoring and alerting system"""
    
    def __init__(self):
        # Configuration
        self.error_threshold = int(os.getenv("ERROR_THRESHOLD", "10"))
        self.time_window = int(os.getenv("TIME_WINDOW", "300"))  # 5 minutes
        self.brute_force_threshold = int(os.getenv("BRUTE_FORCE_THRESHOLD", "5"))
        self.rate_limit_abuse_threshold = int(os.getenv("RATE_LIMIT_ABUSE_THRESHOLD", "3"))
        
        # Data storage
        self.error_patterns: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.request_patterns: Dict[str, List[RequestPattern]] = defaultdict(list)
        self.rate_limit_violations: Dict[str, deque] = defaultdict(lambda: deque(maxlen=50))
        self.alerts: List[SecurityAlert] = []
        
        # Alert suppression
        self.alert_suppression: Dict[str, datetime] = {}
        self.alert_suppression_window = 300  # 5 minutes
        
        # Monitoring metrics
        self.metrics = {
            "total_errors": 0,
            "security_errors": 0,
            "authentication_failures": 0,
            "rate_limit_violations": 0,
            "alerts_generated": 0,
            "suppressed_alerts": 0
        }
    
    def record_error(
        self, 
        error_info: Dict[str, any], 
        ip_address: str, 
        endpoint: str, 
        user_agent: str
    ):
        """Record an error for pattern analysis"""
        current_time = datetime.utcnow()
        
        # Update metrics
        self.metrics["total_errors"] += 1
        if error_info.get("category") == ERROR_CATEGORIES["SECURITY"]:
            self.metrics["security_errors"] += 1
        elif error_info.get("code") in [
            ERROR_CODES["AUTH_INVALID_TOKEN"],
            ERROR_CODES["AUTH_EXPIRED_TOKEN"]
        ]:
            self.metrics["authentication_failures"] += 1
        
        # Store error pattern
        error_pattern = {
            "timestamp": current_time,
            "error_code": error_info.get("code"),
            "category": error_info.get("category"),
            "severity": error_info.get("severity"),
            "endpoint": endpoint,
            "ip_address": ip_address
        }
        
        self.error_patterns[ip_address].append(error_pattern)
        
        # Check for security patterns
        self._check_security_patterns(ip_address, error_info, endpoint, user_agent)
    
    def record_rate_limit_violation(self, ip_address: str, endpoint: str):
        """Record a rate limit violation"""
        current_time = datetime.utcnow()
        
        self.metrics["rate_limit_violations"] += 1
        
        violation = {
            "timestamp": current_time,
            "endpoint": endpoint,
            "ip_address": ip_address
        }
        
        self.rate_limit_violations[ip_address].append(violation)
        
        # Check for rate limit abuse patterns
        self._check_rate_limit_abuse(ip_address)
    
    def record_request(
        self, 
        ip_address: str, 
        endpoint: str, 
        method: str, 
        status_code: int, 
        user_agent: str
    ):
        """Record a request for pattern analysis"""
        current_time = datetime.utcnow()
        
        pattern = RequestPattern(
            ip_address=ip_address,
            endpoint=endpoint,
            method=method,
            timestamp=current_time,
            status_code=status_code,
            user_agent=user_agent
        )
        
        self.request_patterns[ip_address].append(pattern)
        
        # Clean old patterns
        cutoff_time = current_time - timedelta(minutes=60)
        self.request_patterns[ip_address] = [
            p for p in self.request_patterns[ip_address] 
            if p.timestamp > cutoff_time
        ]
    
    def get_security_status(self) -> Dict[str, any]:
        """Get current security status and metrics"""
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Count recent errors
        recent_errors = 0
        for ip_errors in self.error_patterns.values():
            recent_errors += len([
                e for e in ip_errors 
                if e["timestamp"] > one_hour_ago
            ])
        
        # Count recent rate limit violations
        recent_violations = 0
        for ip_violations in self.rate_limit_violations.values():
            recent_violations += len([
                v for v in ip_violations 
                if v["timestamp"] > one_hour_ago
            ])
        
        # Analyze risk level
        risk_level = self._calculate_risk_level(recent_errors, recent_violations)
        
        return {
            "timestamp": current_time.isoformat(),
            "metrics": self.metrics.copy(),
            "active_monitoring": {
                "tracked_ips": len(self.error_patterns),
                "recent_errors": recent_errors,
                "recent_violations": recent_violations,
                "active_alerts": len([a for a in self.alerts if a.timestamp > one_hour_ago]),
                "risk_level": risk_level
            },
            "alerts": [
                {
                    "type": alert.alert_type.value,
                    "severity": alert.severity.value,
                    "message": alert.message,
                    "ip": alert.ip_address,
                    "timestamp": alert.timestamp.isoformat(),
                    "risk_score": alert.risk_score
                }
                for alert in self.alerts[-10:]  # Last 10 alerts
            ]
        }
    
    def get_threat_indicators(self) -> Dict[str, any]:
        """Get threat indicators and suspicious activities"""
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Find IPs with suspicious patterns
        suspicious_ips = {}
        
        for ip_address, errors in self.error_patterns.items():
            recent_errors = [
                e for e in errors 
                if e["timestamp"] > one_hour_ago
            ]
            
            if len(recent_errors) > 5:
                suspicious_ips[ip_address] = {
                    "error_count": len(recent_errors),
                    "error_types": list(set(e["error_code"] for e in recent_errors)),
                    "endpoints": list(set(e["endpoint"] for e in recent_errors)),
                    "last_seen": max(e["timestamp"] for e in recent_errors).isoformat()
                }
        
        # Check rate limit violations
        for ip_address, violations in self.rate_limit_violations.items():
            recent_violations = [
                v for v in violations 
                if v["timestamp"] > one_hour_ago
            ]
            
            if len(recent_violations) > 3:
                if ip_address not in suspicious_ips:
                    suspicious_ips[ip_address] = {"error_count": 0, "error_types": [], "endpoints": [], "last_seen": ""}
                
                suspicious_ips[ip_address].update({
                    "rate_limit_violations": len(recent_violations),
                    "violation_endpoints": list(set(v["endpoint"] for v in recent_violations))
                })
        
        return {
            "timestamp": current_time.isoformat(),
            "suspicious_ips": suspicious_ips,
            "recommendations": self._generate_recommendations(suspicious_ips)
        }
    
    def _check_security_patterns(
        self, 
        ip_address: str, 
        error_info: Dict[str, any], 
        endpoint: str, 
        user_agent: str
    ):
        """Check for security patterns and generate alerts"""
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Get recent errors for this IP
        ip_errors = [
            e for e in self.error_patterns[ip_address] 
            if e["timestamp"] > one_hour_ago
        ]
        
        # Check for brute force attacks
        auth_failures = [
            e for e in ip_errors 
            if e["error_code"] in [
                ERROR_CODES["AUTH_INVALID_TOKEN"],
                ERROR_CODES["AUTH_EXPIRED_TOKEN"]
            ]
        ]
        
        if len(auth_failures) >= self.brute_force_threshold:
            self._generate_alert(
                AlertType.BRUTE_FORCE,
                AlertSeverity.HIGH,
                f"Potential brute force attack detected from {ip_address}",
                ip_address,
                {"failure_count": len(auth_failures), "endpoint": endpoint},
                risk_score=80
            )
        
        # Check for error spikes
        if len(ip_errors) >= self.error_threshold:
            self._generate_alert(
                AlertType.ERROR_SPIKE,
                AlertSeverity.MEDIUM,
                f"High error rate detected from {ip_address}",
                ip_address,
                {"error_count": len(ip_errors), "time_window": "1 hour"},
                risk_score=60
            )
        
        # Check for suspicious input patterns
        if any("SQL" in error_info.get("message", "") or "injection" in error_info.get("message", "").lower()):
            self._generate_alert(
                AlertType.INVALID_INPUT_PATTERN,
                AlertSeverity.CRITICAL,
                f"Potential SQL injection attempt from {ip_address}",
                ip_address,
                {"error_code": error_info.get("code"), "endpoint": endpoint},
                risk_score=90
            )
        
        # Check for path traversal attempts
        if error_info.get("code") == ERROR_CODES["PATH_TRAVERSAL_ATTEMPT"]:
            self._generate_alert(
                AlertType.SUSPICIOUS_REQUEST,
                AlertSeverity.HIGH,
                f"Path traversal attempt detected from {ip_address}",
                ip_address,
                {"endpoint": endpoint, "error_code": error_info.get("code")},
                risk_score=75
            )
    
    def _check_rate_limit_abuse(self, ip_address: str):
        """Check for rate limit abuse patterns"""
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        violations = [
            v for v in self.rate_limit_violations[ip_address] 
            if v["timestamp"] > one_hour_ago
        ]
        
        if len(violations) >= self.rate_limit_abuse_threshold:
            self._generate_alert(
                AlertType.RATE_LIMIT_ABUSE,
                AlertSeverity.MEDIUM,
                f"Rate limit abuse detected from {ip_address}",
                ip_address,
                {"violation_count": len(violations), "time_window": "1 hour"},
                risk_score=50
            )
    
    def _generate_alert(
        self, 
        alert_type: AlertType, 
        severity: AlertSeverity, 
        message: str, 
        ip_address: str, 
        details: Dict[str, any], 
        risk_score: int = 0
    ):
        """Generate a security alert"""
        current_time = datetime.utcnow()
        
        # Check for alert suppression
        suppression_key = f"{alert_type.value}_{ip_address}"
        if suppression_key in self.alert_suppression:
            if current_time < self.alert_suppression[suppression_key]:
                self.metrics["suppressed_alerts"] += 1
                return
        
        # Create alert
        alert = SecurityAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            ip_address=ip_address,
            timestamp=current_time,
            details=details,
            risk_score=risk_score
        )
        
        self.alerts.append(alert)
        self.metrics["alerts_generated"] += 1
        
        # Log the alert
        monitoring_logger.warning(
            f"SECURITY_ALERT - Type: {alert_type.value}, "
            f"Severity: {severity.value}, "
            f"Message: {message}, "
            f"IP: {ip_address}, "
            f"Risk: {risk_score}, "
            f"Details: {details}"
        )
        
        # Set suppression window
        self.alert_suppression[suppression_key] = current_time + timedelta(seconds=self.alert_suppression_window)
    
    def _calculate_risk_level(self, recent_errors: int, recent_violations: int) -> str:
        """Calculate overall risk level"""
        risk_score = (recent_errors * 10) + (recent_violations * 20)
        
        if risk_score >= 200:
            return "CRITICAL"
        elif risk_score >= 100:
            return "HIGH"
        elif risk_score >= 50:
            return "MEDIUM"
        elif risk_score >= 20:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_recommendations(self, suspicious_ips: Dict) -> List[str]:
        """Generate security recommendations"""
        recommendations = []
        
        if suspicious_ips:
            recommendations.append("Review access logs for suspicious IP addresses")
            recommendations.append("Consider implementing IP-based rate limiting")
            recommendations.append("Monitor authentication patterns for anomalies")
        
        if len(suspicious_ips) > 5:
            recommendations.append("Consider implementing temporary IP blocking")
            recommendations.append("Review security rules and input validation")
        
        if any(ip_info.get("rate_limit_violations", 0) > 5 for ip_info in suspicious_ips.values()):
            recommendations.append("Implement stricter rate limiting policies")
        
        return recommendations
    
    def cleanup_old_data(self):
        """Clean up old monitoring data"""
        current_time = datetime.utcnow()
        cutoff_time = current_time - timedelta(hours=24)
        
        # Clean error patterns
        for ip_address in list(self.error_patterns.keys()):
            self.error_patterns[ip_address] = deque([
                e for e in self.error_patterns[ip_address] 
                if e["timestamp"] > cutoff_time
            ], maxlen=100)
            
            if len(self.error_patterns[ip_address]) == 0:
                del self.error_patterns[ip_address]
        
        # Clean rate limit violations
        for ip_address in list(self.rate_limit_violations.keys()):
            self.rate_limit_violations[ip_address] = deque([
                v for v in self.rate_limit_violations[ip_address] 
                if v["timestamp"] > cutoff_time
            ], maxlen=50)
            
            if len(self.rate_limit_violations[ip_address]) == 0:
                del self.rate_limit_violations[ip_address]
        
        # Clean request patterns
        for ip_address in list(self.request_patterns.keys()):
            self.request_patterns[ip_address] = [
                p for p in self.request_patterns[ip_address] 
                if p.timestamp > cutoff_time
            ]
            
            if len(self.request_patterns[ip_address]) == 0:
                del self.request_patterns[ip_address]
        
        # Clean old alerts
        self.alerts = [
            a for a in self.alerts 
            if a.timestamp > cutoff_time
        ]
        
        # Clean alert suppression
        self.alert_suppression = {
            k: v for k, v in self.alert_suppression.items() 
            if v > current_time
        }


# Global security monitor instance
security_monitor = SecurityMonitor()


# Periodic cleanup task
def cleanup_monitoring_data():
    """Clean up old monitoring data periodically"""
    security_monitor.cleanup_old_data()