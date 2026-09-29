from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router


app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="AI-powered comic story and image generator.",
    version="1.0.0",
)

# Static files
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

# Routes
app.include_router(router)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": "ComicCraft"
    }