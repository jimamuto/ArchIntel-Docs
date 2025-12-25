"""
Secure subprocess execution utilities to prevent command injection attacks.
Provides safe subprocess execution with input validation, timeout handling,
and comprehensive security logging.
"""

import subprocess
import logging
import shlex
import tempfile
import os
import signal
import asyncio
from typing import List, Dict, Optional, Union, Any
from pathlib import Path

logger = logging.getLogger("archintel.subprocess_security")
security_logger = logging.getLogger("archintel.security")

class SecurityError(Exception):
    """Custom exception for subprocess security violations."""
    pass

class CommandValidationError(Exception):
    """Custom exception for command validation failures."""
    pass

class SubprocessSecurityConfig:
    """Configuration for subprocess security settings."""
    
    # Allowed commands and their expected argument patterns
    ALLOWED_COMMANDS = {
        'git': {
            'clone': {
                'min_args': 3,
                'max_args': 5,
                'allowed_options': ['--depth', '--single-branch', '--branch', '--origin']
            },
            'fetch': {
                'min_args': 1,
                'max_args': 3,
                'allowed_options': ['--depth', '--single-branch', '--prune']
            },
            'pull': {
                'min_args': 0,
                'max_args': 2,
                'allowed_options': ['--rebase', '--ff-only']
            }
        }
    }
    
    # Maximum execution time in seconds
    MAX_TIMEOUT = 300  # 5 minutes
    
    # Maximum command length
    MAX_COMMAND_LENGTH = 1000
    
    # Allowed characters for command arguments (basic whitelist)
    ALLOWED_CHAR_PATTERN = r'^[a-zA-Z0-9._/-]+$'
    
    # Rate limiting (commands per time window)
    RATE_LIMIT_WINDOW = 60  # seconds
    RATE_LIMIT_MAX = 10     # commands per window


class SecureSubprocess:
    """Secure subprocess execution wrapper with comprehensive security measures."""
    
    def __init__(self, config: Optional[SubprocessSecurityConfig] = None):
        self.config = config or SubprocessSecurityConfig()
        self.command_history = []
        
    def validate_command(self, cmd: Union[str, List[str]], timeout: Optional[int] = None) -> None:
        """
        Validate command and arguments for security compliance.
        
        Args:
            cmd: Command to execute (string or list)
            timeout: Execution timeout in seconds
            
        Raises:
            CommandValidationError: If command fails validation
        """
        if not cmd:
            raise CommandValidationError("Empty command not allowed")
            
        # Validate timeout
        if timeout and timeout > self.config.MAX_TIMEOUT:
            raise CommandValidationError(f"Timeout too high: {timeout}s (max: {self.config.MAX_TIMEOUT}s)")
            
        # Convert to list for processing
        cmd_list = cmd if isinstance(cmd, list) else shlex.split(cmd)
        
        if len(cmd_list) == 0:
            raise CommandValidationError("Empty command list not allowed")
            
        # Validate command length
        if len(' '.join(cmd_list)) > self.config.MAX_COMMAND_LENGTH:
            raise CommandValidationError(f"Command too long: {len(' '.join(cmd_list))} chars (max: {self.config.MAX_COMMAND_LENGTH})")
            
        # Check rate limiting
        self._check_rate_limit()
        
        # Validate command structure
        command_name = cmd_list[0]
        if command_name not in self.config.ALLOWED_COMMANDS:
            raise CommandValidationError(f"Command '{command_name}' not in allowed commands")
            
        # Validate subcommand if present
        if len(cmd_list) > 1:
            subcommand = cmd_list[1]
            if subcommand not in self.config.ALLOWED_COMMANDS[command_name]:
                raise CommandValidationError(f"Subcommand '{subcommand}' not allowed for '{command_name}'")
                
        # Validate arguments
        self._validate_arguments(command_name, cmd_list)
        
        # Log security event
        security_logger.info(f"Command validated: {' '.join(cmd_list)}")
        
    def _validate_arguments(self, command: str, cmd_list: List[str]) -> None:
        """Validate command arguments against security policies."""
        if len(cmd_list) < 2:
            return
            
        subcommand = cmd_list[1]
        allowed_config = self.config.ALLOWED_COMMANDS[command][subcommand]
        
        # Check argument count
        min_args = allowed_config['min_args']
        max_args = allowed_config['max_args']
        actual_args = len(cmd_list) - 2  # Exclude command and subcommand
        
        if actual_args < min_args or actual_args > max_args:
            raise CommandValidationError(f"Invalid argument count for {command} {subcommand}: {actual_args} (expected {min_args}-{max_args})")
            
        # Validate options and arguments
        for i in range(2, len(cmd_list)):
            arg = cmd_list[i]
            
            # Check for dangerous patterns
            dangerous_patterns = ['&', '|', ';', '$(', '`', '>', '<', '&&', '||']
            for pattern in dangerous_patterns:
                if pattern in arg:
                    raise CommandValidationError(f"Dangerous pattern detected in argument: {pattern}")
                    
            # Validate URL format for git clone operations
            if command == 'git' and subcommand == 'clone' and i == 3:  # URL argument
                self._validate_git_url(arg)
                
            # Validate options
            if arg.startswith('--'):
                if arg not in allowed_config['allowed_options']:
                    raise CommandValidationError(f"Option '{arg}' not allowed for {command} {subcommand}")
                    
    def _validate_git_url(self, url: str) -> None:
        """Validate git repository URL format."""
        import re
        
        # HTTPS and SSH URL patterns
        https_pattern = r'^https://(github\.com|gitlab\.com|bitbucket\.org)/[a-zA-Z0-9._/-]+\.git$'
        ssh_pattern = r'^git@(github\.com|gitlab\.com|bitbucket\.org):[a-zA-Z0-9._/-]+\.git$'
        
        if not (re.match(https_pattern, url) or re.match(ssh_pattern, url)):
            raise CommandValidationError(f"Invalid git URL format: {url}")
            
        # Check for allowed domains
        allowed_domains = ['github.com', 'gitlab.com', 'bitbucket.org']
        domain = url.split('@')[-1].split(':')[0].split('/')[0] if '@' in url else url.split('://')[1].split('/')[0]
        
        if domain not in allowed_domains:
            raise CommandValidationError(f"Domain '{domain}' not in allowed domains: {allowed_domains}")
            
    def _check_rate_limit(self) -> None:
        """Check if command execution rate limit is exceeded."""
        import time
        
        current_time = time.time()
        window_start = current_time - self.config.RATE_LIMIT_WINDOW
        
        # Remove old entries
        self.command_history = [t for t in self.command_history if t > window_start]
        
        # Check limit
        if len(self.command_history) >= self.config.RATE_LIMIT_MAX:
            raise CommandValidationError(f"Rate limit exceeded: {self.config.RATE_LIMIT_MAX} commands per {self.config.RATE_LIMIT_WINDOW}s")
            
        self.command_history.append(current_time)
        
    def execute(self, cmd: Union[str, List[str]], 
                capture_output: bool = True, 
                timeout: Optional[int] = None,
                env: Optional[Dict[str, str]] = None,
                cwd: Optional[str] = None) -> subprocess.CompletedProcess:
        """
        Execute a command with security validation and monitoring.
        
        Args:
            cmd: Command to execute
            capture_output: Whether to capture stdout/stderr
            timeout: Execution timeout in seconds
            env: Environment variables
            cwd: Working directory
            
        Returns:
            CompletedProcess object with safe output handling
            
        Raises:
            SecurityError: If security validation fails
            subprocess.TimeoutExpired: If command times out
            subprocess.CalledProcessError: If command returns non-zero exit code
        """
        try:
            # Validate command
            self.validate_command(cmd, timeout)
            
            # Prepare environment
            safe_env = self._sanitize_environment(env)
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=timeout or self.config.MAX_TIMEOUT,
                env=safe_env,
                cwd=cwd,
                check=False  # Don't auto-raise on non-zero exit codes
            )
            
            # Sanitize output
            sanitized_result = self._sanitize_output(result)
            
            # Log execution
            logger.info(f"Command executed successfully: {cmd[0] if isinstance(cmd, list) else cmd.split()[0]}")
            
            return sanitized_result
            
        except (CommandValidationError, subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
            security_logger.error(f"Command execution failed: {str(e)}")
            raise SecurityError(f"Security violation or execution error: {str(e)}")
            
    def _sanitize_environment(self, env: Optional[Dict[str, str]]) -> Dict[str, str]:
        """Sanitize environment variables for security."""
        safe_env = os.environ.copy()
        
        if env:
            # Only allow safe environment variables
            safe_keys = ['PATH', 'HOME', 'USER', 'LANG', 'LC_ALL']
            for key, value in env.items():
                if key in safe_keys and isinstance(value, str) and len(value) < 1000:
                    safe_env[key] = value
                    
        # Set security-focused defaults
        safe_env['GIT_TERMINAL_PROMPT'] = '0'
        safe_env['GIT_SSH_COMMAND'] = 'ssh -o StrictHostKeyChecking=no'
        
        return safe_env
        
    def _sanitize_output(self, result: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
        """Sanitize command output to prevent information leakage."""
        # Remove sensitive information from stdout
        if result.stdout:
            sanitized_stdout = self._remove_sensitive_info(result.stdout)
            result.stdout = sanitized_stdout
            
        # Remove sensitive information from stderr
        if result.stderr:
            sanitized_stderr = self._remove_sensitive_info(result.stderr)
            result.stderr = sanitized_stderr
            
        return result
        
    def _remove_sensitive_info(self, text: str) -> str:
        """Remove sensitive information from output text."""
        import re
        
        # Remove GitHub tokens
        text = re.sub(r'ghp_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
        text = re.sub(r'gho_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
        text = re.sub(r'ghu_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
        text = re.sub(r'ghs_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
        text = re.sub(r'ghr_[a-zA-Z0-9]{36}', '[REDACTED_GITHUB_TOKEN]', text)
        
        # Remove other common token patterns
        text = re.sub(r'[a-zA-Z0-9]{40}', '[REDACTED_TOKEN]', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED_EMAIL]', text)
        
        # Remove IP addresses
        text = re.sub(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', '[REDACTED_IP]', text)
        
        # Remove file paths that might contain sensitive information
        text = re.sub(r'/home/[^/\s]+', '/home/[REDACTED_USER]', text)
        text = re.sub(r'/Users/[^/\s]+', '/Users/[REDACTED_USER]', text)
        
        return text


# Global secure subprocess instance
secure_subprocess = SecureSubprocess()


async def execute_subprocess_async(cmd: Union[str, List[str]], 
                                   timeout: Optional[int] = None,
                                   cwd: Optional[str] = None) -> subprocess.CompletedProcess:
    """
    Execute subprocess command asynchronously with security measures.
    
    Args:
        cmd: Command to execute
        timeout: Execution timeout in seconds
        cwd: Working directory
        
    Returns:
        CompletedProcess object
        
    Raises:
        SecurityError: If security validation fails
    """
    loop = asyncio.get_event_loop()
    
    try:
        # Run in thread pool executor
        result = await loop.run_in_executor(
            None,
            secure_subprocess.execute,
            cmd,
            True,  # capture_output
            timeout,
            None,  # env
            cwd
        )
        return result
        
    except Exception as e:
        logger.error(f"Async subprocess execution failed: {str(e)}")
        raise SecurityError(f"Subprocess execution failed: {str(e)}")


def execute_git_clone(repo_url: str, target_dir: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Execute git clone command with security validation.
    
    Args:
        repo_url: Repository URL to clone
        target_dir: Target directory for clone
        timeout: Execution timeout in seconds
        
    Returns:
        CompletedProcess object
        
    Raises:
        SecurityError: If security validation fails
    """
    cmd = ['git', 'clone', '--depth', '1', repo_url, target_dir]
    return secure_subprocess.execute(cmd, timeout=timeout)


def execute_git_command(repo_path: str, command: str, args: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """
    Execute git command in repository with security validation.
    
    Args:
        repo_path: Path to git repository
        command: Git subcommand
        args: Arguments for the git command
        timeout: Execution timeout in seconds
        
    Returns:
        CompletedProcess object
        
    Raises:
        SecurityError: If security validation fails
    """
    cmd = ['git', command] + args
    return secure_subprocess.execute(cmd, timeout=timeout, cwd=repo_path)