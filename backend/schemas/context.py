"""
Context and Integration Models for ArchIntel Backend

This module contains Pydantic models for context-related API endpoints
with comprehensive input validation and security constraints.
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator
from enum import Enum

from .security import BaseValidationModel, SecurityValidationConfig


class SourceType(str, Enum):
    """Supported source types for discussions"""
    GITHUB_PR = "github_pr"
    GITHUB_ISSUE = "github_issue"


class IngestRequest(BaseValidationModel):
    """Request model for discussion ingestion"""
    
    limit: int = Field(
        default=30,
        ge=1,
        le=100,
        description="Maximum number of discussions to ingest"
    )


class DiscussionSearchRequest(BaseValidationModel):
    """Request model for discussion search"""
    
    source: Optional[SourceType] = Field(
        None,
        description="Source type filter (github_pr, github_issue)"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
    query: Optional[str] = Field(
        None,
        max_length=200,
        description="Search query for title/content"
    )
    
    @validator('query')
    def validate_search_query(cls, v):
        """Validate search query"""
        if v and any(pattern in v for pattern in ['<script>', 'javascript:', 'data:']):
            raise ValueError("Search query contains invalid content")
        
        return v.strip() if v else v


class RationaleRequest(BaseValidationModel):
    """Request model for design rationale generation"""
    
    include_prs: bool = Field(
        default=True,
        description="Include PRs in rationale analysis"
    )
    include_issues: bool = Field(
        default=True,
        description="Include issues in rationale analysis"
    )
    max_discussions: int = Field(
        default=50,
        ge=1,
        le=200,
        description="Maximum discussions to analyze"
    )


class DiscussionResponse(BaseModel):
    """Response model for discussions"""
    
    discussions: List[dict] = Field(
        default=[],
        description="List of discussions"
    )
    total: int = Field(
        default=0,
        description="Total number of discussions"
    )


class RationaleResponse(BaseModel):
    """Response model for design rationale"""
    
    rationale: str = Field(
        ...,
        description="Generated design rationale"
    )
    discussions_count: int = Field(
        ...,
        description="Number of discussions analyzed"
    )
    analysis_period: str = Field(
        default="",
        description="Time period covered by analysis"
    )


class GitHistoryRequest(BaseValidationModel):
    """Request model for Git history operations"""
    
    commit_hash: Optional[str] = Field(
        None,
        min_length=7,
        max_length=40,
        description="Specific commit hash"
    )
    file_path: Optional[str] = Field(
        None,
        max_length=500,
        description="File path for file-specific history"
    )
    path: Optional[str] = Field(
        None,
        max_length=500,
        description="Path for path-specific history"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of commits"
    )
    
    @validator('commit_hash')
    def validate_commit_hash(cls, v):
        """Validate commit hash format"""
        if v:
            import re
            if not re.match(r'^[a-f0-9]{7,40}$', v):
                raise ValueError("Invalid commit hash format")
        return v
    
    @validator('file_path', 'path')
    def validate_file_path(cls, v):
        """Validate file/path"""
        if v:
            import os
            
            # Normalize path
            normalized = os.path.normpath(v)
            
            # Check for traversal
            if '..' in normalized:
                raise ValueError("Path contains traversal attempt")
            
            # Check for absolute paths (should be relative)
            if os.path.isabs(normalized):
                raise ValueError("Path must be relative")
            
            # Check for special files
            if v.startswith('.') or v.endswith('.git'):
                raise ValueError("Access to system files is not allowed")
        
        return v


class AuthorStatsRequest(BaseValidationModel):
    """Request model for author statistics"""
    
    path: Optional[str] = Field(
        None,
        max_length=500,
        description="File or directory path for statistics"
    )
    author: Optional[str] = Field(
        None,
        max_length=200,
        description="Specific author to analyze"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum commits to analyze"
    )
    
    @validator('path')
    def validate_path(cls, v):
        """Validate path"""
        if v:
            import os
            
            # Normalize path
            normalized = os.path.normpath(v)
            
            # Check for traversal
            if '..' in normalized:
                raise ValueError("Path contains traversal attempt")
            
            # Check for absolute paths
            if os.path.isabs(normalized):
                raise ValueError("Path must be relative")
        
        return v


class CommitDiffRequest(BaseValidationModel):
    """Request model for commit diff"""
    
    commit_hash: str = Field(
        ...,
        min_length=7,
        max_length=40,
        description="Commit hash"
    )
    file_path: Optional[str] = Field(
        None,
        max_length=500,
        description="Specific file for diff"
    )
    
    @validator('commit_hash')
    def validate_commit_hash(cls, v):
        """Validate commit hash format"""
        import re
        if not re.match(r'^[a-f0-9]{7,40}$', v):
            raise ValueError("Invalid commit hash format")
        return v
    
    @validator('file_path')
    def validate_file_path(cls, v):
        """Validate file path"""
        if v:
            import os
            
            # Normalize path
            normalized = os.path.normpath(v)
            
            # Check for traversal
            if '..' in normalized:
                raise ValueError("File path contains traversal attempt")
            
            # Check for absolute paths
            if os.path.isabs(normalized):
                raise ValueError("File path must be relative")
        
        return v