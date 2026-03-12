"""WebSocket endpoint — real-time alert push to browser clients.

Flow:
  1. Browser connects to  ws://host/ws/alerts?token=<JWT>
  2. This endpoint subscribes to Redis channel 'alerts' in a background thread
  3. Every alert published by AlertEngine is forwarded to all connected clients
  4. On disconnect the subscription is cleaned up automatically

Multiple tabs / users can connect simultaneously — each gets a separate
subscription.  Redis pub/sub is used as the decoupling layer so the pipeline
(separate process/thread) never has direct WebSocket knowledge.
"""
import json
import asyncio
import threading
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from loguru import logger

from app.core.security import decode_access_token

router = APIRouter()

REDIS_ALERT_CHANNEL = "alerts"


def _get_redis():
    try:
        import redis as _redis
        from app.core.config import settings
        return _redis.from_url(settings.REDIS_URL, decode_responses=True)
    except Exception:
        return None


@router.websocket("/alerts")
async def websocket_alerts(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
):
    """
    Real-time alert stream.

    Connect with:
        ws://localhost:8000/ws/alerts?token=<JWT>

    Each message is JSON:
        {
            "alert_id": 42,
            "rule_id": 1,
            "video_id": 3,
            "behavior_type": "falling",
            "confidence": 0.921,
            "triggered_at": "2026-03-12T01:23:45.678"
        }
    """
    # ── Auth ──────────────────────────────────────────────────────────────────
    if token:
        try:
            payload = decode_access_token(token)
            user_id = payload.get("sub")
        except Exception:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    else:
        # Allow unauthenticated in dev; tighten this for production
        user_id = "anon"

    await websocket.accept()
    logger.info(f"WS /alerts: user={user_id} connected")

    # ── Redis pubsub in a background thread ───────────────────────────────────
    r = _get_redis()
    if r is None:
        # Redis not available — send a warning and keep connection alive
        await websocket.send_text(json.dumps({"error": "Redis unavailable — alerts will not stream"}))
        try:
            while True:
                await asyncio.sleep(30)
        except WebSocketDisconnect:
            pass
        return

    loop = asyncio.get_event_loop()
    queue: asyncio.Queue = asyncio.Queue()

    def _subscribe():
        pubsub = r.pubsub()
        pubsub.subscribe(REDIS_ALERT_CHANNEL)
        for message in pubsub.listen():
            if message["type"] == "message":
                loop.call_soon_threadsafe(queue.put_nowait, message["data"])
            if _stop.is_set():
                pubsub.unsubscribe()
                break

    _stop = threading.Event()
    t = threading.Thread(target=_subscribe, daemon=True)
    t.start()

    # ── Forward queue messages to WebSocket ───────────────────────────────────
    try:
        while True:
            # Wait for next alert (with periodic ping to detect dead connections)
            try:
                data = await asyncio.wait_for(queue.get(), timeout=20.0)
                await websocket.send_text(data)
            except asyncio.TimeoutError:
                # Send a ping to keep the connection alive
                await websocket.send_text(json.dumps({"ping": True}))
    except WebSocketDisconnect:
        logger.info(f"WS /alerts: user={user_id} disconnected")
    except Exception as e:
        logger.warning(f"WS /alerts error: {e}")
    finally:
        _stop.set()
