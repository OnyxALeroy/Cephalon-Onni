import threading
import time
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from database.dynamic.auth import create_token, decode_token
from database.dynamic.crud import create_user, get_user_by_email
from database.dynamic.security import verify_password
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from models.users import UserCreate
from motor.motor_asyncio import AsyncIOMotorClient
from routers import inventory, protected, user, auth


# Connecting to the db
@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.client = AsyncIOMotorClient("mongodb://mongodb:27017")
    application.state.db = application.state.client["cephalon_onni"]
    yield
    application.state.client.close()


# Create app then serve static files
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, wide open
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(inventory.router)
app.include_router(protected.router)
app.include_router(user.router)
app.include_router(auth.router)


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


# -------------------------------------------------------------------------------------------------


def open_browser():
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:8000")


if __name__ == "__main__":
    threading.Thread(target=open_browser).start()

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # production mode
        workers=1,  # can increase if needed
    )
