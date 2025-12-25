"""
Project Management Models for ArchIntel Backend

This module contains Pydantic models for project-related API endpoints
with comprehensive input validation and security constraints.
"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, validator
from enum import Enum

from .security import BaseValidationModel, SecurityValidationConfig


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    READY = "ready"
    ERROR = "error"
    SYNCING = "syncing"


class ProjectCreateRequest(BaseValidationModel):
    """Request model for project creation"""
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=200,
        description="Project name (1-200 characters)"
    )
    repo_url: str = Field(
        ..., 
        description="Repository URL"
    )
    github_token: Optional[str] = Field(
        None,
        max_length=500,
        description="GitHub Personal Access Token for private repos"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate project name format"""
        if not v.strip():
            raise ValueError("Project name cannot be empty")
        
        # Remove special characters that could be problematic
        import re
        if re.search(r'[<>:"/\\|?*]', v):
            raise ValueError("Project name contains invalid characters")
        
        return v.strip()
    
    @validator('repo_url')
    def validate_repo_url(cls, v):
        """Validate repository URL format"""
        import re
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://(github\.com|gitlab\.com|bitbucket\.org)/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+/?$'
        )
        
        if not url_pattern.match(v):
            raise ValueError("Invalid repository URL format")
        
        return v.strip()
    
    @validator('github_token')
    def validate_github_token(cls, v):
        """Validate GitHub token format"""
        if v and not v.startswith('ghp_') and not v.startswith('gho_'):
            raise ValueError("Invalid GitHub token format")
        
        return v


class ProjectIngestRequest(BaseValidationModel):
    """Request model for code ingestion"""
    
    repo_path: str = Field(
        ..., 
        description="Local repository path"
    )
    
    @validator('repo_path')
    def validate_repo_path(cls, v):
        """Validate repository path"""
        # Check for path traversal attempts
        import os
        normalized_path = os.path.normpath(v)
        
        # Check for absolute paths (should be relative or specific patterns)
        if os.path.isabs(normalized_path):
            # Allow absolute paths only in specific directories
            allowed_prefixes = ['/app/repos', '/tmp/repos', '/var/repos']
            if not any(normalized_path.startswith(prefix) for prefix in allowed_prefixes):
                raise ValueError("Repository path must be relative or in allowed directories")
        
        # Check for traversal patterns
        if '..' in normalized_path:
            raise ValueError("Repository path contains invalid traversal patterns")
        
        return normalized_path


class ProjectSyncRequest(BaseValidationModel):
    """Request model for project synchronization"""
    
    force: bool = Field(
        default=False,
        description="Force synchronization even if project is up to date"
    )


class ProjectPathRequest(BaseValidationModel):
    """Request model for file operations with path validation"""
    
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


class ProjectIdRequest(BaseValidationModel):
    """Request model for project ID validation"""
    
    project_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Project ID"
    )
    
    @validator('project_id')
    def validate_project_id(cls, v):
        """Validate project ID format"""
        import re
        
        # Allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Project ID contains invalid characters")
        
        return v


class ProjectSearchRequest(BaseValidationModel):
    """Request model for project search"""
    
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
        if any(char in v for char in ['<script>', 'javascript:', 'data:']):
            raise ValueError("Search query contains invalid content")
        
        return v.strip()


class ProjectUpdateRequest(BaseValidationModel):
    """Request model for project updates"""
    
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Updated project name"
    )
    status: Optional[ProjectStatus] = Field(
        None,
        description="Updated project status"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate project name format"""
        if v and not v.strip():
            raise ValueError("Project name cannot be empty")
        
        import re
        if v and re.search(r'[<>:"/\\|?*]', v):
            raise ValueError("Project name contains invalid characters")
        
        return v.strip() if v else v