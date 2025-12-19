from app.ws.websocket import manager
from app.nats.nats_client import publish_rate

async def notify_rate_event(event: str, rate_data):
    
    if hasattr(rate_data, 'id'): 
        message = {
            "event": event,
            "id": rate_data.id,
            "code": rate_data.code,
            "name": rate_data.name,
            "value": rate_data.value,
            "created_at": rate_data.created_at.isoformat() if rate_data.created_at else None
        }
    elif isinstance(rate_data, dict): 
        message = {
            "event": event,
            **rate_data
        }
    else:
        raise ValueError(f"Unsupported rate data type: {type(rate_data)}")
    
    await publish_rate(message)