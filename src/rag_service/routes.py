from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from rag_service.api_keys.routes import router as api_keys_router
from rag_service.auth.routes import router as auth_router
from rag_service.chats.routes import router as chats_router
from rag_service.config import settings
from rag_service.documents.routes import router as documents_router
from rag_service.embedding_models.routes import router as embedding_models_router
from rag_service.knowledge_bases.routes import router as knowledge_bases_router
from rag_service.llm_models.routes import llm_models_router, models_router
from rag_service.providers.routes import router as providers_router
from rag_service.schema import HealthCheck
from rag_service.users.routes import router as users_router
from rag_service.utils import is_dev_env

router = APIRouter(tags=["Monitoring"], include_in_schema=is_dev_env())


@router.get(
    "/healthcheck",
    responses={
        200: {
            "description": "Service is running",
        },
    },
)
async def healthcheck() -> HealthCheck:
    """
    Checks whether the API service is operational and responding
    """
    return HealthCheck()


@router.get("/docs", include_in_schema=False)
async def scalar_html():
    """
    Serves the Scalar API documentation page.
    """
    return get_scalar_api_reference(
        openapi_url=f"{settings.ROOT_PATH}/openapi.json",
        title="Knowledge Gateway API",
    )


@router.get("/docs/scalar", include_in_schema=False)
async def redirect_to_docs(request: Request):
    """
    Redirects to the Scalar API documentation page.
    """
    docs_url = str(request.url_for("scalar_html"))
    return RedirectResponse(url=docs_url)


def routes_register(app: FastAPI) -> None:
    """
    Registers all API routes with the FastAPI application.
    """
    app.include_router(router=router)
    app.include_router(router=auth_router)
    app.include_router(router=users_router)
    app.include_router(router=api_keys_router)
    app.include_router(router=documents_router)
    app.include_router(router=providers_router)
    app.include_router(router=embedding_models_router)
    app.include_router(router=knowledge_bases_router)
    app.include_router(router=llm_models_router)
    app.include_router(router=models_router)
    app.include_router(router=chats_router)
