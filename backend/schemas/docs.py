"""
Documentation and Analysis Models for ArchIntel Backend

This module contains Pydantic models for documentation-related API endpoints
with comprehensive input validation and security constraints.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum

from .security import BaseValidationModel, SecurityValidationConfig


class DiagramType(str, Enum):
    """Supported diagram types"""
    FLOWCHART = "flowchart"
    SEQUENCE = "sequence"
    CLASS = "class"
    ACTIVITY = "activity"


class FileDocumentationRequest(BaseValidationModel):
    """Request model for file documentation"""
    
    path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="File path relative to repository"
    )
    repo_path: str = Field(
        ...,
        description="Local repository path"
    )
    
    @validator('path')
    def validate_file_path(cls, v):
        """Validate file path"""
        import os
        
        # Normalize path
        normalized = os.path.normpath(v)
        
        # Check for traversal
        if '..' in normalized:
            raise ValueError("File path contains traversal attempt")
        
        # Check for absolute paths
        if os.path.isabs(normalized):
            raise ValueError("File path must be relative")
        
        # Check for special files
        if v.startswith('.') or v.endswith('.git'):
            raise ValueError("Access to system files is not allowed")
        
        return normalized


class FileDocumentationUpdate(BaseValidationModel):
    """Request model for updating file documentation"""
    
    path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="File path relative to repository"
    )
    content: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="Documentation content"
    )
    
    @validator('content')
    def validate_content(cls, v):
        """Validate documentation content"""
        # Remove potentially harmful patterns
        if any(pattern in v for pattern in ['<script>', 'javascript:', 'data:']):
            raise ValueError("Documentation contains invalid content")
        
        return v.strip()


class DiagramRequest(BaseValidationModel):
    """Request model for generating diagrams"""
    
    path: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="File path relative to repository"
    )
    repo_path: str = Field(
        ...,
        description="Local repository path"
    )
    type: DiagramType = Field(
        default=DiagramType.FLOWCHART,
        description="Type of diagram to generate"
    )


class SearchRequest(BaseValidationModel):
    """Request model for documentation search"""
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Search query"
    )
    page: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Page number"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Results per page"
    )
    
    @validator('query')
    def validate_search_query(cls, v):
        """Validate search query"""
        # Remove potentially harmful patterns
        if any(pattern in v for pattern in ['<script>', 'javascript:', 'data:']):
            raise ValueError("Search query contains invalid content")
        
        return v.strip()


class SystemDocumentationRequest(BaseValidationModel):
    """Request model for system documentation"""
    
    repo_path: str = Field(
        ...,
        description="Local repository path"
    )
    
    @validator('repo_path')
    def validate_repo_path(cls, v):
        """Validate repository path"""
        import os
        
        # Basic path validation
        if not v or len(v.strip()) < 1:
            raise ValueError("Repository path cannot be empty")
        
        normalized = os.path.normpath(v.strip())
        
        # Check for traversal
        if '..' in normalized:
            raise ValueError("Repository path contains traversal attempt")
        
        return normalized


class DocumentationSearchResponse(BaseModel):
    """Response model for documentation search"""
    
    files: List[dict] = Field(
        default=[],
        description="Matching files"
    )
    documentation: List[dict] = Field(
        default=[],
        description="Matching documentation snippets"
    )
    total: int = Field(
        default=0,
        description="Total number of results"
    )


class DiagramResponse(BaseModel):
    """Response model for diagram generation"""
    
    diagram: str = Field(
        ...,
        description="Generated Mermaid diagram code"
    )
    type: str = Field(
        ...,
        description="Type of diagram generated"
    )
    file_path: str = Field(
        ...,
        description="File path used for diagram generation"
    )


class DocumentationResponse(BaseModel):
    """Response model for documentation generation"""
    
    content: str = Field(
        ...,
        description="Generated documentation content"
    )
    file_path: str = Field(
        ...,
        description="File path documented"
    )
    language: str = Field(
        ...,
        description="Detected programming language"
    )


class SystemDocumentationResponse(BaseModel):
    """Response model for system documentation"""
    
    content: str = Field(
        ...,
        description="Generated system documentation"
    )
    project_name: str = Field(
        ...,
        description="Project name"
    )
    file_count: int = Field(
        ...,
        description="Number of files analyzed"
    )
    languages: List[str] = Field(
        default=[],
        description="Detected programming languages"
    )