import time
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from routers import (
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


# Add validation error handler for better 422 responses
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error for {request.method} {request.url}: {exc.errors()}")

    # Extract field-specific errors for better user messages
    error_details = []
    for error in exc.errors():
        field = error["loc"][-1] if error["loc"] else "unknown"
        message = error["msg"]

        if "name" in field.lower() and (
            "empty" in message.lower() or "required" in message.lower()
        ):
            error_details.append("Build name is required")
        elif "warframe" in field.lower() and (
            "empty" in message.lower() or "required" in message.lower()
        ):
            error_details.append("Warframe selection is required")
        else:
            error_details.append(f"{field}: {message}")

    return JSONResponse(status_code=422, content={"detail": "; ".join(error_details)})


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
