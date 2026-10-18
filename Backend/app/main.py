from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.claims import router as claims_router
from app.api.stats import router as stats_router
from app.db.session import check_db_connection

app = FastAPI(
    title="SachCheck Backend",
    description="SachCheck automated fact checking backend service",
    version="1.0.0",
)

# Register API routers
app.include_router(claims_router)
app.include_router(stats_router)



@app.get("/health")
def health():
    return {"status": "ok", "project": "SachCheck"}


@app.get("/health/db")
def health_db():
    is_connected, message = check_db_connection()
    status_code = 200 if is_connected else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if is_connected else "error",
            "project": "SachCheck",
            "database": message,
        },
    )
