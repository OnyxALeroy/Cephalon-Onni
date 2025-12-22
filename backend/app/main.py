import threading
import time
import webbrowser
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient
from routers import auth, graph, inventory, protected, user


# Connecting to the db
@asynccontextmanager
async def lifespan(application: FastAPI):
    # Initialize MongoDB connection
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

app.include_router(graph.router)
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
