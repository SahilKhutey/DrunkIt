# FACCP Realtime Service

WebSockets & SSE Engine for Order Status Updates & Live Driver GPS Geolocation Streaming.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| WS | /api/v1/realtime/ws/orders/{order_id} | ✓ | WebSocket live stream for order status updates |
| WS | /api/v1/realtime/ws/driver/{driver_id} | ✓ | WebSocket live stream for driver GPS location |
| POST | /api/v1/realtime/broadcast | Services | Broadcast event data to WebSocket topic |
| GET | /api/v1/realtime/stats | Operations | Get active channel and connection statistics |

## Development

```bash
# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8012 --reload
```
