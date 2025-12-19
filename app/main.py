import asyncio
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.db.session import engine
from app.tasks.background_tasks import rates_background_task
from app.api import rates_endpoint as rates_api
from app.ws import websocket as ws_routes
from app.nats.nats_client import connect_nats
from app.api import tasks_endpoint as tasks_api

app = FastAPI(title="Currency Rates API")

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    asyncio.create_task(rates_background_task())
    asyncio.create_task(connect_nats())

app.include_router(rates_api.router)
app.include_router(tasks_api.router)
app.include_router(ws_routes.router)
