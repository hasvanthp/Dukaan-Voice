from fastapi import FastAPI

from app.api.routes.conversation import router as conversation_router
from app.api.routes.credits import router as credits_router
from app.api.routes.health import router as health_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.sales import router as sales_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging()
app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health_router)
app.include_router(inventory_router, prefix=settings.api_prefix)
app.include_router(sales_router, prefix=settings.api_prefix)
app.include_router(credits_router, prefix=settings.api_prefix)
app.include_router(conversation_router, prefix=settings.api_prefix)
