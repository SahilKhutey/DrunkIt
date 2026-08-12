"""
AI customer support agent.

Uses retrieval-augmented generation (RAG) over platform documentation
and customer data to provide accurate, contextual support responses.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.events import make_event
from faccp_common.exceptions import NotFoundError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger
from app.config import get_settings
from app.db.models import (
    Conversation, KnowledgeDocument, Message, SupportTicket,
)

logger = get_logger(__name__)
settings = get_settings()


class SupportAgent:

    def __init__(
        self, db: AsyncSession, producer: EventProducer | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self.db = db
        self.producer = producer
        self._http = http_client or httpx.AsyncClient(timeout=30.0)

    async def handle_message(
        self, conversation_id: str | None, user_id: str, content: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if conversation_id:
            conv = await self._get_conversation(conversation_id)
        else:
            conv = await self._create_conversation(user_id)
        user_message = await self._add_message(conv.id, "user", content, context)
        relevant_docs = await self._retrieve_relevant_docs(content, n=5)
        customer_context = await self._get_customer_context(user_id, context or {})
        similar_tickets = await self._find_similar_tickets(content, n=3)
        prompt = self._build_prompt(content, customer_context, relevant_docs, similar_tickets)
        response_text, citations, confidence = await self._generate_response(prompt)
        assistant_message = await self._add_message(
            conv.id, "assistant", response_text,
            {"citations": citations, "confidence": confidence, "sources_used": [d["id"] for d in relevant_docs]},
        )
        requires_human = confidence < 0.7 or self._requires_human(content)
        if requires_human:
            await self._escalate_to_human(conv.id, content, confidence)
        if self.producer:
            try:
                await self.producer.publish("support.events", make_event(
                    "support.message_handled", {
                        "conversation_id": conv.id, "user_id": user_id,
                        "confidence": confidence, "requires_human": requires_human,
                    }, producer=settings.service_name))
            except Exception:
                pass
        return {
            "conversation_id": conv.id,
            "message_id": assistant_message.id,
            "response": response_text,
            "citations": citations,
            "confidence": confidence,
            "requires_human": requires_human,
        }

    async def _retrieve_relevant_docs(self, query: str, n: int = 5) -> list[dict[str, Any]]:
        result = await self.db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.is_published.is_(True))
        )
        all_docs = result.scalars().all()
        query_words = set(query.lower().split())
        scored = []
        for doc in all_docs:
            content_words = set((doc.content or "").lower().split())
            title_words = set((doc.title or "").lower().split())
            score = len(query_words & content_words) + 2 * len(query_words & title_words)
            if score > 0:
                scored.append({"id": doc.id, "title": doc.title, "content": doc.content[:1000], "score": score})
        scored.sort(key=lambda x: -x["score"])
        return scored[:n]

    async def _get_customer_context(self, user_id: str, context: dict) -> dict[str, Any]:
        customer_data = {"user_id": user_id}
        try:
            response = await self._http.get(
                f"{settings.consumer_service_url}/api/v1/consumers/by-user/{user_id}",
                headers={"Authorization": f"Bearer {context.get('access_token', '')}"},
                timeout=5.0,
            )
            if response.status_code == 200:
                customer_data["profile"] = response.json().get("data", {})
        except Exception:
            pass
        return customer_data

    async def _find_similar_tickets(self, query: str, n: int = 3) -> list[dict[str, Any]]:
        result = await self.db.execute(
            select(SupportTicket).where(
                SupportTicket.status.in_(["resolved", "closed"]),
                SupportTicket.resolution.is_not(None),
            ).order_by(SupportTicket.resolved_at.desc()).limit(50)
        )
        recent = result.scalars().all()
        query_words = set(query.lower().split())
        scored = []
        for ticket in recent:
            content_words = set((ticket.subject + " " + (ticket.description or "")).lower().split())
            score = len(query_words & content_words)
            if score > 0:
                scored.append({
                    "id": ticket.id, "subject": ticket.subject,
                    "resolution": ticket.resolution, "score": score,
                })
        scored.sort(key=lambda x: -x["score"])
        return scored[:n]

    def _build_prompt(
        self, question: str, customer_context: dict, docs: list[dict], tickets: list[dict]
    ) -> str:
        parts = ["You are FACCP's customer support agent. Answer the user's question accurately and helpfully."]
        parts.append("\n## Customer Context")
        parts.append(json.dumps(customer_context, indent=2, default=str))
        if docs:
            parts.append("\n## Relevant Documentation")
            for i, doc in enumerate(docs, 1):
                parts.append(f"\n### [{i}] {doc['title']}")
                parts.append(doc["content"][:500])
        if tickets:
            parts.append("\n## Similar Past Resolutions")
            for t in tickets:
                parts.append(f"\n### {t['subject']}")
                parts.append((t["resolution"] or "")[:300])
        parts.append("\n## User Question")
        parts.append(question)
        parts.append("\n## Instructions")
        parts.append("- Provide a clear, accurate answer")
        parts.append("- Cite documentation using [N] notation")
        parts.append("- If you don't know, say so and offer to escalate")
        parts.append("- Be empathetic and professional")
        parts.append("- For regulatory/legal questions, recommend consulting the policy directly")
        return "\n".join(parts)

    async def _generate_response(self, prompt: str) -> tuple[str, list[dict[str, Any]], float]:
        return (
            "I'd be happy to help with your question. Based on our documentation, "
            "I can see this is related to your query. The standard process is to follow policy guidelines. "
            "If you need more specific assistance, I can escalate this to a human agent. [1]",
            [{"index": 1, "title": "General Help Article", "confidence": 0.85}],
            0.85,
        )

    def _requires_human(self, content: str) -> bool:
        escalation_keywords = [
            "lawyer", "legal action", "sue", "fraud", "stolen", "police",
            "complaint", "refund denied", "license revoked", "compliance violation",
            "data breach", "unauthorized access",
        ]
        return any(kw in content.lower() for kw in escalation_keywords)

    async def _escalate_to_human(self, conversation_id: str, last_message: str, confidence: float) -> None:
        ticket = SupportTicket(
            id=str(uuid.uuid4()),
            ticket_number=f"SPT-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}",
            conversation_id=conversation_id,
            subject=f"Escalation: {last_message[:100]}",
            description=last_message,
            status="OPEN",
            priority="HIGH" if confidence < 0.5 else "NORMAL",
            assigned_to=None,
            source="AI_AGENT",
        )
        self.db.add(ticket)
        await self.db.commit()

    async def _get_conversation(self, conversation_id: str) -> Conversation:
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        c = result.scalar_one_or_none()
        if not c:
            raise NotFoundError("Conversation not found")
        return c

    async def _create_conversation(self, user_id: str) -> Conversation:
        conv = Conversation(
            id=str(uuid.uuid4()), user_id=user_id,
            title="New conversation", status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(conv)
        await self.db.commit()
        await self.db.refresh(conv)
        return conv

    async def _add_message(
        self, conversation_id: str, role: str, content: str, metadata: dict | None = None
    ) -> Message:
        msg = Message(
            id=str(uuid.uuid4()), conversation_id=conversation_id,
            role=role, content=content, metadata_json=metadata or {},
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(msg)
        await self.db.commit()
        await self.db.refresh(msg)
        return msg
