from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.models.currency import CurrencyRate
from app.tasks.background_tasks import save_rates_to_db
from app.ws.websocket import manager
from app.nats.nats_client import publish_rate
from pydantic import BaseModel
from app.utils.notify import notify_rate_event

router = APIRouter(prefix="/rates", tags=["rates"])

class CurrencyRateCreate(BaseModel):
    code: str
    name: str
    value: float

class CurrencyRateUpdate(BaseModel):
    name: str | None = None
    value: float | None = None

@router.get("/get", response_model=List[CurrencyRate])
async def get_rates(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurrencyRate).order_by(CurrencyRate.created_at.desc())
    )
    return result.scalars().all()

@router.get("/get/code", response_model=List[CurrencyRate])
async def get_rates_by_code(code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CurrencyRate)
        .where(CurrencyRate.code == code.upper())
        .order_by(CurrencyRate.created_at.desc())
    )
    rates = result.scalars().all()
    if not rates:
        raise HTTPException(404, "Currency not found")
    return rates

@router.post("/create", response_model=CurrencyRate)
async def create_rate(rate: CurrencyRateCreate, db: AsyncSession = Depends(get_db)):
    obj = CurrencyRate(**rate.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)

    await notify_rate_event("rate_created", obj)
    return obj

@router.patch("/update", response_model=CurrencyRate)
async def update_rate(rate_id: int, rate: CurrencyRateUpdate, db: AsyncSession = Depends(get_db)):
    obj = await db.get(CurrencyRate, rate_id)
    if not obj:
        raise HTTPException(404, "Rate not found")

    for key, value in rate.model_dump(exclude_unset=True).items():
        setattr(obj, key, value)

    await db.commit()
    await db.refresh(obj)

    await notify_rate_event("rate_updated", obj)
    return obj

@router.delete("/delete", status_code=204)
async def delete_rate(rate_id: int, db: AsyncSession = Depends(get_db)):
    obj = await db.get(CurrencyRate, rate_id)
    if not obj:
        raise HTTPException(404, "Rate not found")
    await db.delete(obj)
    await db.commit()

    await notify_rate_event("rate_deleted", obj)

