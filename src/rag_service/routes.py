from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import RedirectResponse
from scalar_fastapi import get_scalar_api_reference

from rag_service.config import settings
from rag_service.schema import HealthCheck
from rag_service.users.routes import router as users_router

router = APIRouter(tags=["Monitoring"])


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
        title="RAG Service API",
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
    app.include_router(router=users_router)
