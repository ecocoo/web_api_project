import asyncio
from app.services.parser import RatesParser
from app.db.session import AsyncSessionLocal
from app.models.currency import CurrencyRate
from app.nats.nats_client import publish_rate
from sqlalchemy import select
from app.utils.notify import notify_rate_event

UPDATE_INTERVAL = 600  # секунд

async def save_rates_to_db():
    parser = RatesParser()
    rates = await parser.fetch_rates() 

    saved_rates = []

    async with AsyncSessionLocal() as db:
        for rate in rates:
            result = await db.execute(
                select(CurrencyRate)
                .where(CurrencyRate.code == rate["code"])
                .order_by(CurrencyRate.created_at.desc())
            )
            last_rate = result.scalars().first()

            if last_rate:
                if last_rate.value == rate["value"]:
                    print(f"[BackgroundTask] {rate['code']} курс не изменился ({rate['value']})")
                    continue

            obj = CurrencyRate(
                code=rate["code"],
                name=rate["name"],
                value=rate["value"]
            )
            db.add(obj)
            saved_rates.append(obj)

        await db.commit()
        for obj in saved_rates:
            await db.refresh(obj)

    for obj in saved_rates:
        await notify_rate_event("rate_updated", obj)

    return saved_rates

async def rates_background_task():
    while True:
        try:
            await save_rates_to_db()
        except Exception as e:
            print(f"[RatesTask] error: {e}")
        await asyncio.sleep(UPDATE_INTERVAL)
