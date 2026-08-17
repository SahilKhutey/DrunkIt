from datetime import datetime, timezone
from services.security.app.engine.velocity_engine import VelocityEngine
from services.security.app.services.risk_service import RiskService


class SecurityEventConsumer:

    def __init__(self, risk_service: RiskService | None = None, velocity_engine: VelocityEngine | None = None):
        self.risk_service = risk_service or RiskService()
        self.velocity_engine = velocity_engine or VelocityEngine()
        self.processed_events: set[str] = set()

    async def handle_event(self, event: dict) -> bool:
        event_id = event.get("event_id") or event.get("id")
        if event_id and event_id in self.processed_events:
            return False  # Idempotent rejection of duplicate event

        if event_id:
            self.processed_events.add(event_id)

        event_type = event.get("type") or event.get("event")

        if event_type == "order.created":
            consumer_id = event.get("consumer_id") or event.get("subject_id")
            if consumer_id:
                sig = await self.velocity_engine.check_order_velocity(consumer_id)
                if sig:
                    await self.risk_service.add_signal("CONSUMER", consumer_id, sig["signal_type"], sig["score"], sig["severity"])

        elif event_type == "payment.failed":
            consumer_id = event.get("consumer_id") or event.get("subject_id")
            if consumer_id:
                await self.risk_service.add_signal("CONSUMER", consumer_id, "PAYMENT_FAILURE", 10.0, "MEDIUM")

        elif event_type == "verification.failed":
            consumer_id = event.get("consumer_id") or event.get("subject_id")
            if consumer_id:
                await self.risk_service.add_signal("CONSUMER", consumer_id, "VERIFICATION_FAILED", 20.0, "HIGH")

        return True
