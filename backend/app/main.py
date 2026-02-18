import asyncio
import logging
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
    worldstate,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    from database.db import db_manager

    db_manager.initialize()

    application.state.client = db_manager.async_client
    application.state.db = db_manager.async_db

    from services.worldstate import (
        WorldStateCache,
        WorldStateFetcher,
        set_worldstate_cache,
    )

    collection = db_manager.async_db["worldstate"]
    cache = WorldStateCache(collection)
    await cache.connect()
    set_worldstate_cache(cache)

    fetcher = WorldStateFetcher(cache)
    fetch_task = asyncio.create_task(_run_fetcher_with_lock(cache, fetcher))

    yield

    fetcher.stop_requested = True
    fetch_task.cancel()
    try:
        await fetch_task
    except asyncio.CancelledError:
        pass
    await cache.disconnect()
    db_manager.close_all()


async def _run_fetcher_with_lock(cache, fetcher):
    import redis.asyncio as aioredis

    LOCK_KEY = "worldstate:fetcher_lock"
    LOCK_TTL = 10

    try:
        r = await cache._get_redis()
        await r.ping()
    except Exception:
        logger.info("Redis unavailable, running fetcher without lock")
        await fetcher.start()
        return

    fetcher.stop_requested = False
    while not getattr(fetcher, "stop_requested", False):
        try:
            lock = r.lock(LOCK_KEY, timeout=LOCK_TTL, blocking=False)
            if await lock.acquire(blocking=False):
                try:
                    logger.info("This worker acquired fetcher lock")
                    while not getattr(fetcher, "stop_requested", False):
                        try:
                            await fetcher._fetch_once()
                        except Exception as e:
                            logger.error(f"WorldState fetch error: {e}")
                        await asyncio.sleep(fetcher.interval)
                finally:
                    try:
                        await lock.release()
                    except Exception:
                        pass
            else:
                await asyncio.sleep(LOCK_TTL / 2)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logger.warning(f"Fetcher lock error: {e}")
            await asyncio.sleep(5)


# Create app then serve static files
app: FastAPI = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing, wide open
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422, content={"detail": "Validation failed", "errors": exc.errors()}
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
app.include_router(worldstate.router)


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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=4,
    )
