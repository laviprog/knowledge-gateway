class AppError(Exception):
    """Base application error. Services only raise subclasses of this."""

    status_code = 400
    code = "app_error"
    default_detail = "An application error occurred"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.default_detail
        super().__init__(self.detail)


class BadRequestError(AppError):
    """Raised when request data is valid syntactically but invalid for business rules."""

    status_code = 400
    code = "bad_request"
    default_detail = "Bad request"


class UnauthorizedError(AppError):
    """Raised when a request lacks valid authentication credentials."""

    status_code = 401
    code = "unauthorized"
    default_detail = "Unauthorized"


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    status_code = 404
    code = "not_found"
    default_detail = "Resource not found"


class PermissionDeniedError(AppError):
    """Raised when a user tries to access a resource they don't have permission for."""

    status_code = 403
    code = "permission_denied"
    default_detail = "Permission denied"


class ConflictError(AppError):
    """Raised when a request conflicts with the current resource state."""

    status_code = 409
    code = "conflict"
    default_detail = "Conflict"
