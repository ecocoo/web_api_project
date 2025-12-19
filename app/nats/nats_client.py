from nats.aio.client import Client as NATS
import json
from app.ws.websocket import manager

nc = NATS()

async def connect_nats():
    await nc.connect("nats://127.0.0.1:4222")
    await nc.subscribe("rates.updates", cb=message_handler)
    print("[NATS] connected and subscribed to 'rates.updates'")

async def publish_rate(rate: dict):
    await nc.publish("rates.updates", json.dumps(rate,ensure_ascii=False).encode('utf-8'))

async def message_handler(msg):
    data = json.loads(msg.data.decode())
    print(f"[NATS] Received: {data}")
    await manager.broadcast(data)
