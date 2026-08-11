import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/catalog-service")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/inventory-service")))

import pytest
from catalog_app.main import CATALOG_DB, get_products, get_product
from inventory_app.main import INVENTORY_DB, reserve_stock, ReserveRequest

def test_catalog_query():
    products = get_products(category="SPIRITS")
    assert len(products) >= 2
    whisky = get_product("SKU-WHISKY-SINGLE-MALT-750")
    assert whisky.name == "Amrut Fusion Single Malt Indian Whisky"
    assert whisky.abv == 50.0

def test_inventory_reservation():
    req = ReserveRequest(store_id="STR-BANGALORE-01", sku="SKU-GIN-CRAFT-750", quantity=2)
    initial_available = INVENTORY_DB["STR-BANGALORE-01"]["SKU-GIN-CRAFT-750"].available_stock
    resp = reserve_stock(req)
    assert resp.success is True
    updated_available = INVENTORY_DB["STR-BANGALORE-01"]["SKU-GIN-CRAFT-750"].available_stock
    assert updated_available == initial_available - 2
