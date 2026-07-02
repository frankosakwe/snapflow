"""
SnapFlow Exception Classes

Custom exception hierarchy for better error handling and debugging.
"""


class SnapFlowError(Exception):
    """Base exception for all SnapFlow errors"""
    pass


class ConfigError(SnapFlowError):
    """Base exception for configuration-related errors"""
    pass


class InvalidConfigError(ConfigError):
    """Raised when configuration is invalid or malformed"""
    
    def __init__(self, message, field=None):
        self.field = field
        super().__init__(message)


class MissingConfigError(ConfigError):
    """Raised when configuration file is not found"""
    
    def __init__(self, message="Configuration file not found. Run 'snapflow init' to create one."):
        super().__init__(message)


class DatabaseError(SnapFlowError):
    """Base exception for database-related errors"""
    pass


class SnapshotNotFoundError(SnapFlowError):
    """Raised when requested snapshot does not exist"""
    
    def __init__(self, snapshot_name):
        self.snapshot_name = snapshot_name
        super().__init__(f"Snapshot '{snapshot_name}' not found")


class SnapshotAlreadyExistsError(SnapFlowError):
    """Raised when trying to create a snapshot that already exists"""
    
    def __init__(self, snapshot_name):
        self.snapshot_name = snapshot_name
        super().__init__(f"Snapshot '{snapshot_name}' already exists")


class DatabaseNotSupportedError(DatabaseError):
    """Raised when database dialect is not supported"""
    
    def __init__(self, dialect):
        self.dialect = dialect
        super().__init__(
            f"Database dialect '{dialect}' is not supported. "
            "Supported dialects: postgresql, mysql"
        )


class DatabaseConnectionError(DatabaseError):
    """Raised when unable to connect to database"""
    
    def __init__(self, url, original_error=None):
        self.url = url
        self.original_error = original_error
        message = f"Unable to connect to database: {url}"
        if original_error:
            message += f"\nError: {str(original_error)}"
        super().__init__(message)


class SnapshotRestoreError(SnapFlowError):
    """Raised when snapshot restore operation fails"""
    
    def __init__(self, snapshot_name, reason):
        self.snapshot_name = snapshot_name
        self.reason = reason
        super().__init__(f"Failed to restore snapshot '{snapshot_name}': {reason}")


class BackgroundProcessError(SnapFlowError):
    """Raised when background process encounters an error"""
    pass
