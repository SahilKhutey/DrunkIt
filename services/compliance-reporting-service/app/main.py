from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.database import get_db_session, get_engine, get_session_factory
from faccp_common.dto import SuccessResponse
from faccp_common.middleware import register_exception_handlers, register_middleware
from app.config import get_settings
from app.services.reporting_service import ComplianceReportingService

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    engine = get_engine(settings.database_url)
    session_factory = get_session_factory(engine)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory
    yield
    await engine.dispose()


app = FastAPI(title="FACCP Compliance Reporting Service", version=settings.service_version, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
register_middleware(app)
register_exception_handlers(app)


async def get_reporting_service(app_state: Any = None) -> AsyncGenerator[ComplianceReportingService, None]:
    pass

@app.get("/api/v1/reports/daily-transaction", response_model=SuccessResponse[dict])
async def get_daily_transaction_report(
    jurisdiction: str = Query(..., min_length=2),
    report_date: date = Query(...),
) -> SuccessResponse[dict]:
    session_factory = app.state.db_session_factory
    async for session in get_db_session(session_factory):
        service = ComplianceReportingService(db=session)
        result = await service.generate_daily_transaction_report(jurisdiction, report_date)
        return SuccessResponse(data=result)


@app.get("/api/v1/reports/sar", response_model=SuccessResponse[dict])
async def get_sar_report(
    jurisdiction: str = Query(..., min_length=2),
    start_date: date = Query(...),
    end_date: date = Query(...),
) -> SuccessResponse[dict]:
    session_factory = app.state.db_session_factory
    async for session in get_db_session(session_factory):
        service = ComplianceReportingService(db=session)
        result = await service.generate_sar_report(jurisdiction, start_date, end_date)
        return SuccessResponse(data=result)


@app.get("/api/v1/reports/audit-integrity", response_model=SuccessResponse[dict])
async def get_audit_integrity_report() -> SuccessResponse[dict]:
    session_factory = app.state.db_session_factory
    async for session in get_db_session(session_factory):
        service = ComplianceReportingService(db=session)
        result = await service.generate_audit_chain_integrity_report()
        return SuccessResponse(data=result)
