from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.musiques import router as musiques_router
from database import init_db, get_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Service BDD - Music Voice App",
    description="API REST pour la gestion des musiques",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(musiques_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")


@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        conn = get_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "service": "service-bdd",
        "version": "1.0.0",
        "endpoints": ["/health", "/musiques", "/musiques/{id}", "/musiques/search?q="]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002)
