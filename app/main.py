import logging
from fastapi import FastAPI

from app.auth_router import router as auth_router
from app.task_router import router as task_router
from app.logging_config import setup_logging

setup_logging()

logger = logging.getLogger(__name__)
app = FastAPI()
logger.info("Task Management API started")

app.include_router(auth_router)
app.include_router(task_router)


@app.get("/")
async def root():
    return {"message": "Task Management API is running!"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/version")
async def version():
    return {"version": "1.0.0"}