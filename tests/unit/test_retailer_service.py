import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/retailer-service")))

import pytest
from retailer_app.main import STORES_DB, get_store, list_stores

def test_list_stores_karnataka():
    stores = list_stores(jurisdiction="IN-KA")
    assert len(stores) >= 1
    assert stores[0].jurisdiction == "IN-KA"

def test_get_store_license_validity():
    store = get_store("STR-BANGALORE-01")
    assert store.store_id == "STR-BANGALORE-01"
    assert store.license is not None
    assert store.license.status == "ACTIVE"
