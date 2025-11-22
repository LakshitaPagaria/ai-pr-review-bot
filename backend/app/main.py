from fastapi import FastAPI
from .webhook import router as webhook_router
from .api import router as api_router

app = FastAPI(title="AI PR Bot")

# Include routers
app.include_router(webhook_router)
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"status": "ai-pr-bot running"}
