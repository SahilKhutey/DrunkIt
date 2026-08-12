"""
Product Attribute Catalog System.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class AttributeDefinition:
    attribute_id: str
    name: str
    data_type: str
    required: bool = False
    validation_regex: str | None = None


class AttributeCatalog:
    CORE_ATTRIBUTES: ClassVar[dict[str, AttributeDefinition]] = {
        "abv": AttributeDefinition("attr_abv", "Alcohol By Volume", "decimal", required=True),
        "volume_ml": AttributeDefinition("attr_vol", "Volume in Milliliters", "integer", required=True),
        "origin": AttributeDefinition("attr_org", "Country / Region of Origin", "string"),
        "packaging": AttributeDefinition("attr_pkg", "Packaging Type", "enum"),
    }
