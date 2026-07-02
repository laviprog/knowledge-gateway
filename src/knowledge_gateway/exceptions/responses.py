from typing import Any

from knowledge_gateway.exceptions.schema import ErrorResponse, ValidationErrorResponse

OpenAPIResponses = dict[int | str, dict[str, Any]]

bad_request_response: OpenAPIResponses = {
    400: {"model": ErrorResponse, "description": "Bad request"},
}

unauthorized_response: OpenAPIResponses = {
    401: {"model": ErrorResponse, "description": "Unauthorized"},
}

forbidden_response: OpenAPIResponses = {
    403: {"model": ErrorResponse, "description": "Forbidden"},
}

auth_responses: OpenAPIResponses = {
    **unauthorized_response,
    **forbidden_response,
}

not_found_response: OpenAPIResponses = {
    404: {"model": ErrorResponse, "description": "Not found"},
}

conflict_response: OpenAPIResponses = {
    409: {"model": ErrorResponse, "description": "Conflict"},
}

validation_error_response: OpenAPIResponses = {
    422: {"model": ValidationErrorResponse, "description": "Validation error"},
}

internal_server_error_response: OpenAPIResponses = {
    500: {"model": ErrorResponse, "description": "Internal server error"},
}
