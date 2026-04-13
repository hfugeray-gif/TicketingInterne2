from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.tickets import router as tickets_router
from app.api.routes.comments import router as comments_router
from app.api.routes.merge import router as merge_router
from app.api.routes.config import router as config_router


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

# --------------------------------------------------
# 🌐 CORS (important pour front <-> back)
# --------------------------------------------------
origins = [origin.strip() for origin in settings.cors_allow_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# 🔌 Routes API
# --------------------------------------------------
app.include_router(tickets_router, prefix="/tickets", tags=["tickets"])
app.include_router(comments_router, prefix="/comments", tags=["comments"])
app.include_router(merge_router, prefix="/merge", tags=["merge"])
app.include_router(config_router, prefix="/config", tags=["config"])


# --------------------------------------------------
# ❤️ Healthcheck
# --------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


