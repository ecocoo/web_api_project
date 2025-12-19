from fastapi import APIRouter
from app.tasks.background_tasks import save_rates_to_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/run")
async def run_rates_task():
    rates = await save_rates_to_db()
    
    return {
        "status": "success", 
        "message": f"Rates update started, saved {len(rates)} records"
    }