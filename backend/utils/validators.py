"""
Input Validation and Security Module
Prevents crashes, security issues, and resource exhaustion
"""

from pathlib import Path
from typing import Optional, List, Set
import re
import os

class ValidationError(Exception):
    """Base validation exception"""
    pass

class InvalidPathError(ValidationError):
    """Invalid file/folder path"""
    pass

class FileTooLargeError(ValidationError):
    """File exceeds size limit"""
    pass

class UnsupportedFileTypeError(ValidationError):
    """File type not supported"""
    pass

class SecurityError(ValidationError):
    """Security violation detected"""
    pass


class InputValidator:
    """
    Comprehensive input validation with security checks
    """
    
    # Configuration
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB per file
    MAX_TOTAL_SIZE = 500 * 1024 * 1024  # 500MB total per scan
    MAX_FILES_PER_SCAN = 1000
    MAX_PATH_LENGTH = 500
    MAX_QUERY_LENGTH = 500
    
    ALLOWED_EXTENSIONS: Set[str] = {'.pdf', '.docx', '.txt'}
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'\.\.',  # Directory traversal
        r'~',     # Home directory expansion
        r'\$',    # Environment variables
        r'`',     # Command execution
        r'\|',    # Pipe operator
        r';',     # Command chaining
    ]
    
    @staticmethod
    def validate_folder_path(path: str, must_exist: bool = True) -> Path:
        """
        Validate and sanitize folder path with security checks
        """
        # Check length
        if len(path) > InputValidator.MAX_PATH_LENGTH:
            raise InvalidPathError(f"Path too long (max {InputValidator.MAX_PATH_LENGTH} chars)")
        
        # Check for dangerous patterns
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, path):
                raise SecurityError(f"Dangerous pattern detected in path: {pattern}")
        
        try:
            # Convert to absolute path
            p = Path(path).resolve()
            
            # Check if path exists
            if must_exist and not p.exists():
                raise InvalidPathError(f"Path does not exist: {path}")
            
            # Check if it's a directory
            if must_exist and not p.is_dir():
                raise InvalidPathError(f"Path is not a directory: {path}")
            
            # Security: Check if path is under allowed roots
            allowed_roots = InputValidator._get_allowed_roots()
            
            if not any(InputValidator._is_subpath(p, root) for root in allowed_roots):
                raise SecurityError(
                    f"Access denied: Path not in allowed directories. "
                    f"Allowed roots: {[str(r) for r in allowed_roots]}"
                )
            
            return p
            
        except (OSError, RuntimeError) as e:
            raise InvalidPathError(f"Invalid path: {str(e)}")
    
    @staticmethod
    def validate_file_path(path: str) -> Path:
        """Validate individual file path"""
        try:
            p = Path(path).resolve()
            
            if not p.exists():
                raise InvalidPathError(f"File does not exist: {path}")
            
            if not p.is_file():
                raise InvalidPathError(f"Path is not a file: {path}")
            
            return p
            
        except (OSError, RuntimeError) as e:
            raise InvalidPathError(f"Invalid file path: {str(e)}")
    
    @staticmethod
    def validate_file_size(file_path: Path, max_size: Optional[int] = None) -> int:
        """Validate file size"""
        max_size = max_size or InputValidator.MAX_FILE_SIZE
        
        try:
            size = file_path.stat().st_size
            
            if size > max_size:
                size_mb = size / (1024 * 1024)
                max_mb = max_size / (1024 * 1024)
                raise FileTooLargeError(
                    f"File too large: {size_mb:.1f}MB (max {max_mb:.1f}MB)"
                )
            
            return size
            
        except OSError as e:
            raise InvalidPathError(f"Cannot get file size: {str(e)}")
    
    @staticmethod
    def validate_extension(ext: str) -> bool:
        """Check if file extension is supported"""
        if not ext:
            return False
        
        if not ext.startswith('.'):
            ext = '.' + ext
        
        return ext.lower() in InputValidator.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validate and sanitize search query"""
        if not query or not query.strip():
            raise ValidationError("Query cannot be empty")
        
        query = query.strip()
        
        if len(query) > InputValidator.MAX_QUERY_LENGTH:
            raise ValidationError(
                f"Query too long (max {InputValidator.MAX_QUERY_LENGTH} chars)"
            )
        
        sanitized = re.sub(r'[<>{}[\]\\]', '', query)
        
        return sanitized
    
    @staticmethod
    def _get_allowed_roots() -> List[Path]:
        """Get list of allowed root directories"""
        allowed = []
        
        allowed.append(Path.home())
        
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / 'data'
        if data_dir.exists():
            allowed.append(data_dir)
        
        allowed.append(Path.cwd())
        
        if os.name == 'nt':
            docs = Path.home() / 'Documents'
            if docs.exists():
                allowed.append(docs)
            
            desktop = Path.home() / 'Desktop'
            if desktop.exists():
                allowed.append(desktop)
        
        return allowed
    
    @staticmethod
    def _is_subpath(path: Path, parent: Path) -> bool:
        """Check if path is under parent directory"""
        try:
            path.relative_to(parent)
            return True
        except ValueError:
            return False
