"""
Security Models for ArchIntel Backend

This module contains Pydantic models for security validation,
error handling, and configuration management.
"""

import re
from typing import List, Dict, Optional, Union
from pydantic import BaseModel, Field, validator


class SecurityValidationConfig(BaseModel):
    """Security validation configuration"""
    
    max_input_length: int = Field(default=10000, ge=100, le=100000)
    max_query_length: int = Field(default=1000, ge=10, le=10000)
    max_file_path_length: int = Field(default=500, ge=10, le=2000)
    max_repo_path_length: int = Field(default=1000, ge=50, le=5000)
    
    allowed_extensions: List[str] = Field(default=[
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.h', '.hpp',
        '.php', '.rb', '.go', '.rs', '.swift', '.kt', '.scala', '.cs', '.vb',
        '.html', '.htm', '.css', '.scss', '.sass', '.less', '.json', '.xml',
        '.yml', '.yaml', '.md', '.txt', '.sql', '.sh', '.bash', '.zsh'
    ])
    
    blocked_patterns: List[str] = Field(default=[
        r'\.\./', r'\.\.\\', r'%2e%2e/', r'%2e%2e\\', r'\.\.%2f', r'\.\.%5c',
        r'~/', r'/root/', r'/etc/', r'/proc/', r'/sys/', r'/dev/'
    ])
    
    trusted_domains: List[str] = Field(default=['github.com', 'gitlab.com', 'bitbucket.org'])


class ValidationError(BaseModel):
    """Standardized validation error response"""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Human-readable error message")
    field: Optional[str] = Field(None, description="Field that failed validation")
    value: Optional[Union[str, int, float]] = Field(None, description="Value that failed validation")
    timestamp: str = Field(..., description="ISO timestamp of error")
    
    class Config:
        schema_extra = {
            "example": {
                "error": "INVALID_INPUT",
                "message": "Input contains invalid characters or patterns",
                "field": "repo_url",
                "value": "http://example.com/../../../etc/passwd",
                "timestamp": "2025-12-25T10:30:00Z"
            }
        }


class BaseValidationModel(BaseModel):
    """Base class for all validation models with common security checks"""
    
    def __init__(self, **data):
        # Custom validation for string fields
        for field_name, field_value in data.items():
            field_info = self.__fields__.get(field_name)
            if field_info and isinstance(field_value, str):
                self._validate_input_length(field_value, field_name)
                data[field_name] = self.sanitize_string(field_value)
        
        super().__init__(**data)
    
    @classmethod
    def _validate_input_length(cls, value: str, field_name: str):
        """Validate input length for string fields"""
        if not isinstance(value, str):
            return
        
        config = SecurityValidationConfig()
        max_length = getattr(config, f'max_{field_name}_length', config.max_input_length)
        
        if len(value) > max_length:
            raise ValueError(f'{field_name} too long. Maximum length is {max_length} characters.')
    
    @classmethod
    def sanitize_string(cls, value: str) -> str:
        """Sanitize string input to prevent injection attacks"""
        if not isinstance(value, str):
            value = str(value)
        
        config = SecurityValidationConfig()
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32)
        
        # Check for blocked patterns
        for pattern in config.blocked_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise ValueError(f'Input contains blocked pattern: {pattern}')
        
        return sanitized.strip()
    
    @classmethod
    def validate_file_extension(cls, filename: str, allowed_extensions: List[str]) -> bool:
        """Validate file extension against allowed list"""
        import os
        extension = os.path.splitext(filename)[1].lower()
        return extension in [ext.lower() for ext in allowed_extensions]


class PaginationParams(BaseModel):
    """Standard pagination parameters with validation"""
    
    page: int = Field(default=1, ge=1, le=1000)
    limit: int = Field(default=20, ge=1, le=100)
    offset: Optional[int] = Field(default=None, ge=0, le=100000)
    
    @validator('offset')
    def validate_offset(cls, v, values):
        """Validate offset is consistent with page and limit"""
        if v is not None:
            page = values.get('page', 1)
            limit = values.get('limit', 20)
            expected_offset = (page - 1) * limit
            
            if v != expected_offset:
                raise ValueError(f'Offset {v} does not match page {page} and limit {limit}')
        
        return v