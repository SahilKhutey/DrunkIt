"""Support Agent API routes."""

from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_support_agent
from app.schemas.support import (
    SupportMessageRequest, SupportMessageResponse, SupportTicketCreate,
    SupportTicketResponse,
)
from app.services.support_agent import SupportAgent

router = APIRouter(prefix="/support", tags=["AI Support Agent Engine"])


@router.post("/message", response_model=SuccessResponse[SupportMessageResponse])
async def handle_message(
    payload: SupportMessageRequest,
    agent: Annotated[SupportAgent, Depends(get_support_agent)],
) -> SuccessResponse[SupportMessageResponse]:
    res = await agent.handle_message(
        conversation_id=payload.conversation_id,
        user_id=payload.user_id,
        content=payload.content,
        context=payload.context,
    )
    return SuccessResponse(data=SupportMessageResponse(
        conversation_id=res["conversation_id"],
        message_id=res["message_id"],
        response=res["response"],
        citations=res.get("citations", []),
        confidence=res.get("confidence", 1.0),
        requires_human=res.get("requires_human", False),
    ), message="Support message processed")


@router.post("/tickets", response_model=SuccessResponse[SupportTicketResponse], status_code=201)
async def create_ticket(
    payload: SupportTicketCreate,
    agent: Annotated[SupportAgent, Depends(get_support_agent)],
) -> SuccessResponse[SupportTicketResponse]:
    ticket_num = f"TCK-{secrets.token_hex(4).upper()}"
    ticket = await agent.create_ticket(
        ticket_number=ticket_num,
        subject=payload.subject,
        description=payload.description,
        priority=payload.priority,
    )
    return SuccessResponse(data=SupportTicketResponse(
        id=ticket.id, ticket_number=ticket.ticket_number, subject=ticket.subject,
        description=ticket.description, status=ticket.status, priority=ticket.priority,
        created_at=ticket.created_at,
    ), message="Support ticket created")
