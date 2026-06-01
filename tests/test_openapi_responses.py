from typing import Any

from rag_service.main import app


def get_operation_responses(method: str, path: str) -> dict[str, Any]:
    schema = app.openapi()
    return schema["paths"][path][method]["responses"]


def get_optional_operation_responses(method: str, path: str) -> dict[str, Any] | None:
    schema = app.openapi()
    if path not in schema["paths"]:
        return None

    return schema["paths"][path][method]["responses"]


def test_request_body_validation_is_documented_as_422() -> None:
    for method, path in [
        ("post", "/documents"),
        ("post", "/documents/search"),
        ("post", "/llm-models"),
        ("patch", "/llm-models/{model_id}"),
        ("post", "/chat/completions"),
        ("post", "/users"),
        ("patch", "/users/{user_id}"),
        ("post", "/users/{user_id}/api-keys"),
    ]:
        responses = get_optional_operation_responses(method, path)
        if responses is None:
            continue

        assert "422" in responses
        if path != "/chat/completions":
            assert "400" not in responses


def test_document_routes_are_protected() -> None:
    for method, path in [
        ("get", "/documents"),
        ("post", "/documents"),
        ("post", "/documents/search"),
        ("post", "/documents/upload"),
        ("get", "/documents/{document_id}"),
        ("delete", "/documents/{document_id}"),
    ]:
        responses = get_optional_operation_responses(method, path)
        if responses is None:
            continue

        assert "401" in responses
        assert "403" in responses


def test_llm_model_routes_are_protected() -> None:
    for method, path in [
        ("get", "/llm-models"),
        ("post", "/llm-models"),
        ("get", "/llm-models/{model_id}"),
        ("patch", "/llm-models/{model_id}"),
        ("delete", "/llm-models/{model_id}"),
        ("get", "/models"),
    ]:
        responses = get_optional_operation_responses(method, path)
        if responses is None:
            continue

        assert "401" in responses
        assert "403" in responses


def test_chat_completion_routes_are_protected() -> None:
    responses = get_operation_responses("post", "/chat/completions")

    assert "401" in responses
    assert "403" in responses


def test_document_upload_business_errors_are_documented_as_400() -> None:
    responses = get_optional_operation_responses("post", "/documents/upload")
    if responses is None:
        return

    assert "400" in responses


def test_user_state_conflicts_are_documented_as_409() -> None:
    for method, path in [
        ("patch", "/users/{user_id}"),
        ("delete", "/users/{user_id}"),
        ("post", "/llm-models"),
        ("patch", "/llm-models/{model_id}"),
    ]:
        responses = get_optional_operation_responses(method, path)
        if responses is None:
            continue

        assert "409" in responses
