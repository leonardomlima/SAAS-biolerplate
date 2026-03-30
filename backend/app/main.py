import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_router
from app.core.cache import init_redis
from app.core.config import settings
from app.core.tenant import TenantMiddleware

structlog.configure()

app = FastAPI(title=settings.PROJECT_NAME, version="0.1.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TenantMiddleware)
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event() -> None:
    await init_redis()
