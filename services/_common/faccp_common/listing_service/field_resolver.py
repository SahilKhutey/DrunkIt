"""
Field Resolver Registry Pattern.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar
from .context import ListingContext


class BaseFieldResolver(ABC):
    @abstractmethod
    def resolve(self, context: ListingContext) -> Any:
        pass


class ProductNameResolver(BaseFieldResolver):
    def resolve(self, context: ListingContext) -> Any:
        return context.product_data.get("name", "Unknown Product")


class BrandResolver(BaseFieldResolver):
    def resolve(self, context: ListingContext) -> Any:
        return context.product_data.get("brand", "Unknown Brand")


class PriceResolver(BaseFieldResolver):
    def resolve(self, context: ListingContext) -> Any:
        return context.pricing_state.get("selling_price", 0.0)


class FieldResolver:
    """Typed registry mapping field keys to resolver instances."""

    RESOLVERS: ClassVar[dict[str, BaseFieldResolver]] = {
        "name": ProductNameResolver(),
        "brand": BrandResolver(),
        "price": PriceResolver(),
    }

    @classmethod
    def resolve_field(cls, field_name: str, context: ListingContext) -> Any:
        resolver = cls.RESOLVERS.get(field_name)
        if not resolver:
            return None
        return resolver.resolve(context)
