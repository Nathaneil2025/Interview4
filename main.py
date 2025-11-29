from fastapi import FastAPI
from datetime import datetime, timezone

app = FastAPI(
    title="Interview4 App",
    description="DevOps Pipeline Demo Application",
    version="1.0.1"
)


@app.get("/")
def root():
    return {"message": "Welcome to Interview4 App"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/info")
def info():
    return {
        "app": "Interview4",
        "version": "1.0.0",
        "environment": "production"
    }