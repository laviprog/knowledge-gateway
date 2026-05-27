from typing import Any

from rag_service.main import app


def get_operation_responses(method: str, path: str) -> dict[str, Any]:
    schema = app.openapi()
    return schema["paths"][path][method]["responses"]


def test_request_body_validation_is_documented_as_422() -> None:
    for method, path in [
        ("post", "/users"),
        ("patch", "/users/{user_id}"),
        ("post", "/users/{user_id}/api-keys"),
    ]:
        responses = get_operation_responses(method, path)

        assert "422" in responses
        assert "400" not in responses


def test_user_state_conflicts_are_documented_as_409() -> None:
    for method, path in [
        ("patch", "/users/{user_id}"),
        ("delete", "/users/{user_id}"),
    ]:
        responses = get_operation_responses(method, path)

        assert "409" in responses
