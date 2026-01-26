import time
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from routers import (
    admin,
    admin_age,
    auth,
    builds,
    inventory,
    loottables,
    protected,
    user,
    warframes,
)


# Connecting to the db
@asynccontextmanager
async def lifespan(application: FastAPI):
    # Initialize MongoDB connection
    from database.db import db_manager

    db_manager.initialize()

    # Store references in app state for backward compatibility
    application.state.client = db_manager.async_client
    application.state.db = db_manager.async_db

    yield
    # Close connections
    db_manager.close_all()


# Create app then serve static files
app: FastAPI = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, wide open
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(admin_age.router)
app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(loottables.router)
app.include_router(protected.router)
app.include_router(user.router)
app.include_router(builds.router)
app.include_router(warframes.router)


# Serve the main index.html for frontend routes
@app.get("/")
async def serve_index():
    return FileResponse("../frontend/Cephalon-Onni/dist/index.html")


@app.get("/admin")
async def serve_admin():
    return FileResponse("../frontend/Cephalon-Onni/dist/index.html")


@app.get("/login")
async def serve_login():
    return FileResponse("../frontend/Cephalon-Onni/dist/index.html")


@app.get("/register")
async def serve_register():
    return FileResponse("static/index.html")


@app.get("/inventory")
async def serve_inventory():
    return FileResponse("static/index.html")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}


# -------------------------------------------------------------------------------------------------


def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # production mode
        workers=1,  # can increase if needed
    )
