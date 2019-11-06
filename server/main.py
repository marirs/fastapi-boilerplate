"""
CDE v2
"""
from fastapi import FastAPI

from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response

from server.core.settings import default_route_str
from server.api import router as endpoint_router
from server.db.mongodb import close, connect, AsyncIOMotorClient, get_database

import uvicorn


app = FastAPI(title="CDE v2", version="2")
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.include_router(endpoint_router, prefix=default_route_str)


@app.on_event("startup")
async def on_app_start():
    """Anything that needs to be done while app starts
    """
    await connect()


@app.on_event("shutdown")
async def on_app_shutdown():
    """Anything that needs to be done while app shutdown
    """
    await close()


@app.get("/")
async def home():
    """Home page
    """
    return Response("CDE v2")


if __name__ == "__main__":
    uvicorn.run(app, log_level="debug", reload=True)
