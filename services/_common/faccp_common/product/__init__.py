"""Product Platform Package (Truth vs Presentation Separation)."""
from .master import ProductMaster, SKU, ProductLifecycleState, VisibilityLevel
from .projections import ViewComposer, ConsumerProductView, RetailerProductView, AdminProductView, SearchProductView
from .attributes import AttributeCatalog, AttributeDefinition

__all__ = [
    "ProductMaster",
    "SKU",
    "ProductLifecycleState",
    "VisibilityLevel",
    "ViewComposer",
    "ConsumerProductView",
    "RetailerProductView",
    "AdminProductView",
    "SearchProductView",
    "AttributeCatalog",
    "AttributeDefinition",
]
