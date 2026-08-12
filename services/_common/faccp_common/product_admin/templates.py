"""
Listing Template Builder & Low-Code Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar


class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"
    CURRENCY = "currency"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    IMAGE = "image"
    DOCUMENT = "document"
    REFERENCE = "reference"
    COMPUTED = "computed"


class ListingTemplateState(str, Enum):
    DRAFT = "DRAFT"
    TESTING = "TESTING"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"


@dataclass
class TemplateField:
    name: str
    field_type: FieldType
    required: bool = True
    editable: bool = True
    default_value: Any = None


@dataclass
class ListingTemplateBuilder:
    template_id: str
    name: str
    version: str = "1.0"
    state: ListingTemplateState = ListingTemplateState.DRAFT
    fields: list[TemplateField] = field(default_factory=list)

    FIELD_TYPES: ClassVar[list[FieldType]] = list(FieldType)
