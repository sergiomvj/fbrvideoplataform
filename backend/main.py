from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from infrastructure.settings.config import Settings
from infrastructure.logging import configure_logging
from infrastructure.metrics import metrics_collector
from application.errors import AppError, app_error_handler, generic_error_handler
from application.services.media_sourcing import media_sourcing_service
from api.routes.productions import router as productions_router
from api.routes.templates import router as templates_router
from api.routes.renders import router as renders_router
from api.routes.review import router as review_router
from api.routes.media_sourcing import router as media_sourcing_router
from integrations.stock_media import stock_media_adapter
from integrations.archive_media import archive_media_adapter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(json_logs=True)
    media_sourcing_service.register_adapter(stock_media_adapter)
    media_sourcing_service.register_adapter(archive_media_adapter)
    yield


settings = Settings()
app = FastAPI(
    title="Synkra API",
    version="0.1.0",
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, generic_error_handler)


app.include_router(productions_router)
app.include_router(templates_router)
app.include_router(renders_router)
app.include_router(review_router)
app.include_router(media_sourcing_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics", response_class=PlainTextResponse)
async def metrics():
    return PlainTextResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
