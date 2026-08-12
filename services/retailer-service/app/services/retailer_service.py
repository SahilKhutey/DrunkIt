"""Retailer service: Organizations, Store Network, License Tracking, Staff Management."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import (
    RetailerOrganization, Store, StoreLicense, StoreStaffAssignment,
)
from app.schemas.retailer import (
    LicenseCreate, OrganizationCreate, StaffAssignCreate, StoreCreate,
)

logger = get_logger(__name__)
settings = get_settings()


class RetailerService:
    """Retailer organization & store network orchestrator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # ORGANIZATION MANAGEMENT
    # ============================================================
    async def create_organization(self, payload: OrganizationCreate) -> RetailerOrganization:
        existing = await self._get_org_by_gstin(payload.gstin)
        if existing:
            raise ConflictError(f"Organization with GSTIN {payload.gstin} already exists")

        org = RetailerOrganization(
            legal_name=payload.legal_name,
            trade_name=payload.trade_name,
            business_type=payload.business_type,
            gstin=payload.gstin.upper(),
            pan=payload.pan.upper(),
            owner_user_id=payload.owner_user_id,
            seller_level="S1_BASIC",
            is_active=True,
            is_verified=False,
        )
        self.db.add(org)
        await self.db.commit()
        await self.db.refresh(org)

        await self._publish("retailer.org_created", {
            "organization_id": org.id, "legal_name": org.legal_name, "gstin": org.gstin,
        })
        return org

    async def get_organization(self, org_id: str) -> RetailerOrganization:
        result = await self.db.execute(
            select(RetailerOrganization).where(RetailerOrganization.id == org_id)
        )
        org = result.scalar_one_or_none()
        if not org:
            raise NotFoundError(f"Retailer Organization {org_id} not found")
        return org

    # ============================================================
    # STORE NETWORK MANAGEMENT
    # ============================================================
    async def create_store(self, payload: StoreCreate) -> Store:
        org = await self.get_organization(payload.organization_id)

        existing_store = await self._get_store_by_code(payload.code)
        if existing_store:
            raise ConflictError(f"Store code {payload.code} already exists")

        store = Store(
            organization_id=org.id,
            code=payload.code,
            name=payload.name,
            store_type=payload.store_type,
            address_line_1=payload.address_line_1,
            address_line_2=payload.address_line_2,
            city=payload.city,
            state=payload.state,
            pincode=payload.pincode,
            jurisdiction=payload.jurisdiction,
            latitude=payload.latitude,
            longitude=payload.longitude,
            is_active=True,
            is_accepting_orders=True,
        )
        self.db.add(store)
        await self.db.commit()
        await self.db.refresh(store)

        await self._publish("retailer.store_created", {
            "store_id": store.id, "organization_id": store.organization_id, "code": store.code,
        })
        return store

    async def get_store(self, store_id: str) -> Store:
        result = await self.db.execute(select(Store).where(Store.id == store_id))
        store = result.scalar_one_or_none()
        if not store:
            raise NotFoundError(f"Store {store_id} not found")
        return store

    async def list_stores_for_org(self, org_id: str) -> list[Store]:
        result = await self.db.execute(
            select(Store).where(Store.organization_id == org_id).order_by(Store.created_at.desc())
        )
        return list(result.scalars().all())

    # ============================================================
    # EXCISE LICENSE MANAGEMENT
    # ============================================================
    async def add_store_license(self, store_id: str, payload: LicenseCreate) -> StoreLicense:
        store = await self.get_store(store_id)

        existing_lic = await self._get_license_by_number(payload.license_number)
        if existing_lic:
            raise ConflictError(f"License number {payload.license_number} already registered")

        status = "ACTIVE" if payload.valid_until >= date.today() else "EXPIRED"

        lic = StoreLicense(
            store_id=store.id,
            license_number=payload.license_number,
            license_type=payload.license_type,
            issuing_authority=payload.issuing_authority,
            jurisdiction=payload.jurisdiction,
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
            status=status,
            document_url=payload.document_url,
        )
        self.db.add(lic)
        await self.db.commit()
        await self.db.refresh(lic)

        await self._publish("retailer.license_added", {
            "store_id": store.id, "license_number": lic.license_number, "status": status,
        })
        return lic

    async def list_store_licenses(self, store_id: str) -> list[StoreLicense]:
        result = await self.db.execute(
            select(StoreLicense).where(StoreLicense.store_id == store_id)
            .order_by(StoreLicense.valid_until.desc())
        )
        return list(result.scalars().all())

    # ============================================================
    # STORE STAFF ASSIGNMENT
    # ============================================================
    async def assign_staff(self, store_id: str, payload: StaffAssignCreate) -> StoreStaffAssignment:
        store = await self.get_store(store_id)

        assignment = StoreStaffAssignment(
            store_id=store.id,
            user_id=payload.user_id,
            role_in_store=payload.role_in_store,
            is_active=True,
        )
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def list_store_staff(self, store_id: str) -> list[StoreStaffAssignment]:
        result = await self.db.execute(
            select(StoreStaffAssignment).where(
                StoreStaffAssignment.store_id == store_id,
                StoreStaffAssignment.is_active == True,  # noqa: E712
            )
        )
        return list(result.scalars().all())

    # ============================================================
    # HELPERS
    # ============================================================
    async def _get_org_by_gstin(self, gstin: str) -> RetailerOrganization | None:
        result = await self.db.execute(
            select(RetailerOrganization).where(RetailerOrganization.gstin == gstin.upper())
        )
        return result.scalar_one_or_none()

    async def _get_store_by_code(self, code: str) -> Store | None:
        result = await self.db.execute(select(Store).where(Store.code == code))
        return result.scalar_one_or_none()

    async def _get_license_by_number(self, num: str) -> StoreLicense | None:
        result = await self.db.execute(select(StoreLicense).where(StoreLicense.license_number == num))
        return result.scalar_one_or_none()

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-retailer")
            await self.producer.publish("retailer.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
