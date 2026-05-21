class AppError(Exception):
    """Base application error. Services only raise subclasses of this."""

    def __init__(self, detail: str = "An application error occurred"):
        self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail)


class PermissionDeniedError(AppError):
    """Raised when a user tries to access a resource they don't have permission for."""

    def __init__(self, detail: str = "Permission denied"):
        super().__init__(detail)
